"""
Approach 1: Direct LLM matching.

Sends the parsed resume and a job description to the LLM and asks for a
match score with reasoning. Simpler to build, higher per-call cost, but
more nuanced output because the model reasons over the full content.

Use when: low volume, you want detailed explanations, you're iterating on
what "good match" means and benefit from the LLM's judgment.

Avoid when: processing thousands of resumes against one job (costs add up
linearly) or when you need deterministic, reproducible scores.
"""

import json

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

from resume_parser import parse_resume

load_dotenv()
client = OpenAI()


class MatchResult(BaseModel):
    overall_score: int = Field(description="Match score from 0 to 100")
    skills_match: int = Field(description="How well skills align, 0-100")
    experience_match: int = Field(description="How well experience level aligns, 0-100")
    education_match: int = Field(description="How well education aligns, 0-100")
    strengths: list[str] = Field(description="Specific reasons this candidate fits")
    gaps: list[str] = Field(description="Specific gaps or concerns")
    summary: str = Field(description="2-3 sentence overall assessment")


def match_resume_to_job(
    resume_data: dict,
    job_description: str,
    model: str = "gpt-4o-mini",
) -> dict:
    """
    Score how well a parsed resume matches a job description.
    Returns a dict with scores, strengths, gaps, and summary.
    """
    # Pass the structured resume rather than raw text - it's more token-efficient
    # and the model reasons better over clean JSON than over messy extracted text.
    resume_json = json.dumps(resume_data, indent=2)

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an experienced technical recruiter evaluating candidate "
                    "fit against job requirements. Be specific and honest. Do not "
                    "inflate scores. A score of 70 means 'solid fit with some gaps'; "
                    "90+ should be rare and reserved for exceptional alignment. "
                    "Base scores on evidence in the resume, not assumptions."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"JOB DESCRIPTION:\n{job_description}\n\n"
                    f"CANDIDATE RESUME (parsed):\n{resume_json}\n\n"
                    "Evaluate the match."
                ),
            },
        ],
        response_format=MatchResult,
    )

    result = completion.choices[0].message.parsed
    return result.model_dump() if result else None


def rank_candidates(
    resume_paths: list[str],
    job_description: str,
    model: str = "gpt-4o-mini",
) -> list[dict]:
    """
    Parse and rank multiple resumes against a single job description.
    Returns a list of results sorted by overall_score descending.
    """
    results = []
    for path in resume_paths:
        print(f"Parsing {path}...")
        resume = parse_resume(path)
        if resume is None:
            print(f"  Skipped (parse failed)")
            continue

        print(f"  Matching against job...")
        match = match_resume_to_job(resume, job_description, model=model)
        if match is None:
            print(f"  Skipped (match failed)")
            continue

        results.append({
            "path": path,
            "name": resume.get("name", "Unknown"),
            "match": match,
        })

    results.sort(key=lambda r: r["match"]["overall_score"], reverse=True)
    return results


if __name__ == "__main__":
    # Example usage
    example_job = """
    Senior Python Backend Engineer

    We're looking for a backend engineer with 5+ years of Python experience
    to work on our payment processing platform. Required: strong Python,
    experience with PostgreSQL, REST API design, and cloud infrastructure
    (AWS or GCP). Nice to have: fintech background, experience with high-
    throughput systems, Kubernetes.

    Bachelor's degree in CS or equivalent experience.
    """

    import sys
    if len(sys.argv) < 2:
        print("Usage: python match_llm.py <resume1.pdf> [resume2.pdf] ...")
        sys.exit(1)

    rankings = rank_candidates(sys.argv[1:], example_job)

    print("\n" + "=" * 60)
    print("CANDIDATE RANKINGS")
    print("=" * 60)
    for i, r in enumerate(rankings, 1):
        m = r["match"]
        print(f"\n{i}. {r['name']} ({r['path']})")
        print(f"   Overall: {m['overall_score']} | Skills: {m['skills_match']} "
              f"| Experience: {m['experience_match']} | Education: {m['education_match']}")
        print(f"   Summary: {m['summary']}")
        if m['strengths']:
            print(f"   Strengths: {', '.join(m['strengths'][:3])}")
        if m['gaps']:
            print(f"   Gaps: {', '.join(m['gaps'][:3])}")