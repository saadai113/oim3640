"""
Approach 2: Embedding-based matching.

Converts resumes and the job description into vector embeddings, then uses
cosine similarity to rank candidates. Optionally sends top-K candidates to
the LLM for detailed scoring (hybrid approach).

Use when: you have many resumes to rank against a job, or you're building
a searchable candidate database where the same resume gets matched against
many jobs over time.

Key advantage: embeddings are cheap (~$0.02 per 1M tokens) and you only
compute them once per resume. Cosine similarity over numpy arrays is
effectively free compared to LLM calls.

Key limitation: similarity scores are a blunt instrument. They capture
"how similar is the overall text" not "does this candidate meet the
specific requirements." A resume full of buzzwords from the job
description will score high even if the actual experience is thin. This
is why the hybrid approach (embeddings for first-pass, LLM for top-K) is
usually more trustworthy than embeddings alone.
"""

import json
import pickle
from pathlib import Path

import numpy as np
from openai import OpenAI

from resume_parser import parse_resume
from matchllm import match_resume_to_job

client = OpenAI()

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536  # dimensions for text-embedding-3-small


# ---------- Embedding helpers ----------

def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> np.ndarray:
    """Get an embedding vector for a single text."""
    # Truncate to stay well under the 8191 token limit for embedding models.
    # Rough heuristic: 1 token ~= 4 chars, so 30000 chars ~= 7500 tokens.
    if len(text) > 30000:
        text = text[:30000]
    response = client.embeddings.create(model=model, input=text)
    return np.array(response.data[0].embedding, dtype=np.float32)


def get_embeddings_batch(texts: list[str], model: str = EMBEDDING_MODEL) -> np.ndarray:
    """Get embeddings for multiple texts in one API call. More efficient."""
    truncated = [t[:30000] if len(t) > 30000 else t for t in texts]
    response = client.embeddings.create(model=model, input=truncated)
    return np.array([d.embedding for d in response.data], dtype=np.float32)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors. Returns value in [-1, 1]."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def cosine_similarity_batch(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Cosine similarity between one query vector and a matrix of vectors."""
    # Normalize once, then dot product is cosine similarity.
    query_norm = query / np.linalg.norm(query)
    matrix_norm = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix_norm @ query_norm


# ---------- Resume-to-embeddable-text conversion ----------

def resume_to_text(resume_data: dict) -> str:
    """
    Convert a parsed resume dict into a single text string suitable for
    embedding. We construct this deliberately rather than passing raw
    extracted text so that the embedding captures the structured content
    rather than formatting noise.
    """
    parts = [
        f"Name: {resume_data.get('name', '')}",
        f"Summary: {resume_data.get('summary', '')}",
        f"Skills: {', '.join(resume_data.get('skills', []))}",
        f"Years of experience: {resume_data.get('years_of_experience', 0)}",
    ]

    parts.append("Work experience:")
    for job in resume_data.get("work_experience", []):
        parts.append(
            f"- {job.get('title', '')} at {job.get('company', '')} "
            f"({job.get('start_date', '')} to {job.get('end_date', '')}): "
            f"{job.get('description', '')}"
        )

    parts.append("Education:")
    for edu in resume_data.get("education", []):
        parts.append(
            f"- {edu.get('degree', '')} in {edu.get('field_of_study', '')} "
            f"from {edu.get('institution', '')}"
        )

    return "\n".join(parts)


# ---------- Resume database ----------

class ResumeDatabase:
    """
    In-memory store of parsed resumes and their embeddings. Persists to
    disk as a pickle file. At small scale (<10K resumes) this is fine;
    for larger scale, replace with a proper vector DB (Qdrant, Pinecone,
    pgvector, etc.).
    """

    def __init__(self, db_path: str = "resume_db.pkl"):
        self.db_path = db_path
        self.resumes: list[dict] = []  # parsed resume dicts
        self.paths: list[str] = []     # original file paths
        self.embeddings: np.ndarray = np.zeros((0, EMBEDDING_DIM), dtype=np.float32)
        self.load()

    def load(self):
        if Path(self.db_path).exists():
            with open(self.db_path, "rb") as f:
                data = pickle.load(f)
                self.resumes = data["resumes"]
                self.paths = data["paths"]
                self.embeddings = data["embeddings"]
            print(f"Loaded {len(self.resumes)} resumes from {self.db_path}")

    def save(self):
        with open(self.db_path, "wb") as f:
            pickle.dump({
                "resumes": self.resumes,
                "paths": self.paths,
                "embeddings": self.embeddings,
            }, f)

    def add_resume(self, path: str) -> bool:
        """Parse, embed, and store a resume. Returns True on success."""
        if path in self.paths:
            print(f"Already in database: {path}")
            return False

        resume = parse_resume(path)
        if resume is None:
            return False

        text = resume_to_text(resume)
        embedding = get_embedding(text)

        self.resumes.append(resume)
        self.paths.append(path)
        self.embeddings = np.vstack([self.embeddings, embedding[np.newaxis, :]])
        return True

    def add_resumes(self, paths: list[str]):
        """Batch add multiple resumes."""
        for path in paths:
            print(f"Adding {path}...")
            self.add_resume(path)
        self.save()

    def search(self, job_description: str, top_k: int = 10) -> list[dict]:
        """
        Rank resumes by embedding similarity to a job description.
        Returns top_k results with similarity scores.
        """
        if len(self.resumes) == 0:
            return []

        job_embedding = get_embedding(job_description)
        similarities = cosine_similarity_batch(job_embedding, self.embeddings)

        # Get top_k indices by similarity, descending
        top_indices = np.argsort(similarities)[::-1][:top_k]

        return [
            {
                "path": self.paths[i],
                "name": self.resumes[i].get("name", "Unknown"),
                "resume": self.resumes[i],
                "similarity": float(similarities[i]),
            }
            for i in top_indices
        ]


# ---------- Hybrid: embeddings for first-pass, LLM for top-K ----------

def hybrid_rank(
    db: ResumeDatabase,
    job_description: str,
    first_pass_k: int = 20,
    final_k: int = 5,
) -> list[dict]:
    """
    Two-stage ranking:
    1. Use embeddings to cheaply narrow down to first_pass_k candidates.
    2. Use the LLM to score those in detail and return the top final_k.

    This is almost always the right approach at scale - you avoid paying
    for LLM calls on obviously-unqualified candidates, while still getting
    nuanced scoring on the ones that matter.
    """
    # Stage 1: embedding search
    candidates = db.search(job_description, top_k=first_pass_k)
    print(f"Stage 1: narrowed to {len(candidates)} candidates via embeddings")

    # Stage 2: LLM scoring on the narrowed set
    for c in candidates:
        print(f"  Scoring {c['name']}...")
        c["match"] = match_resume_to_job(c["resume"], job_description)

    # Sort by LLM overall_score, fall back to similarity if match failed
    candidates.sort(
        key=lambda c: c["match"]["overall_score"] if c.get("match") else -1,
        reverse=True,
    )

    return candidates[:final_k]


if __name__ == "__main__":
    import sys

    example_job = """
    Senior Python Backend Engineer

    We're looking for a backend engineer with 5+ years of Python experience
    to work on our payment processing platform. Required: strong Python,
    experience with PostgreSQL, REST API design, and cloud infrastructure
    (AWS or GCP). Nice to have: fintech background, experience with high-
    throughput systems, Kubernetes.
    """

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Add resumes:  python match_embeddings.py add <resume1.pdf> ...")
        print("  Search:       python match_embeddings.py search")
        print("  Hybrid rank:  python match_embeddings.py hybrid")
        sys.exit(1)

    db = ResumeDatabase()
    command = sys.argv[1]

    if command == "add":
        db.add_resumes(sys.argv[2:])
        print(f"Database now contains {len(db.resumes)} resumes")

    elif command == "search":
        results = db.search(example_job, top_k=10)
        print("\nEmbedding-only ranking:")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['name']} (similarity: {r['similarity']:.3f}) - {r['path']}")

    elif command == "hybrid":
        results = hybrid_rank(db, example_job, first_pass_k=20, final_k=5)
        print("\nHybrid ranking (embeddings + LLM):")
        for i, r in enumerate(results, 1):
            m = r.get("match", {})
            print(f"\n{i}. {r['name']}")
            print(f"   Similarity: {r['similarity']:.3f} | LLM score: {m.get('overall_score', 'N/A')}")
            print(f"   {m.get('summary', '')}")