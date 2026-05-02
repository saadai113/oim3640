# LLM-Powered Resume Parsing and Candidate-Job Matching

**Author:** Saad Abdullah  
**Institution:** Babson College — OIM3640  
**Date:** April 2026

---

## Overview

A Python pipeline that takes a stack of resumes (PDF, DOCX, RTF, HTML, or plaintext), extracts structured data from each one using GPT-4o-mini, and ranks candidates against a job description. The system includes a Flask web interface and five AI-powered components.

The core technical thesis: modern LLM APIs have shifted applied NLP work from model engineering to system design. No custom training, no GPU, no specialized NLP libraries — just schema design, prompt calibration, cost optimization, and pipeline architecture.

---

## Features

- **Multi-format ingestion** — PDF, DOCX, RTF, HTML, and TXT
- **Structured extraction** — Pydantic-enforced JSON output (name, contact info, work experience, education, skills, years of experience)
- **LLM-based matching** — Overall score plus sub-scores for skills, experience, and education; includes strengths, gaps, and a narrative summary
- **Hybrid matching** — Embedding-based first-pass ranking + LLM scoring on top-K candidates; cuts LLM costs by 90–95%
- **Resume rewriting** — Rewrites bullet points and summary to better match a target role without fabricating anything
- **Data normalization** — Canonical forms for skills, job titles, and institution names
- **Flask web app** — Upload resumes, paste a job description, view ranked results in browser

---

## Architecture

```
resume_parser.py        # Text extraction + structured field parsing (GPT-4o-mini)
matchllm.py             # Direct LLM candidate-job matching with sub-scores
match_embeddings.py     # Embedding similarity + hybrid ranking pipeline
resume_rewriter.py      # Rewrites resume content to target a specific role
normalizer.py           # Canonical normalization for skills, titles, institutions
app.py                  # Flask web interface
templates/index.html    # Frontend
```

### Key Design Decisions

- **Pydantic structured outputs** — the model is constrained to return valid JSON conforming to the schema every time; no post-hoc parsing or validation layer needed
- **Temperature-0 scoring** — resists the score-inflation tendency LLMs have in evaluative tasks; 70 = solid fit with gaps, 90+ is rare
- **Clean text reconstruction** — embeddings are computed on text reconstructed from parsed JSON, not raw PDF extraction output (which contains page numbers, header repetitions, column artifacts)
- **Pickle-based vector store** — works up to ~10,000 resumes before needing migration to a proper vector DB (pgvector, Qdrant)

---

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in this directory:

```
OPENAI_API_KEY=your-key-here
```

---

## Usage

### Web App

```bash
python app.py
```

Open `http://localhost:5000`, upload resumes, paste a job description, and view ranked results.

### Command Line

```bash
# Parse a single resume
python resume_parser.py resume.pdf

# Score a resume against a job description (LLM-only)
python matchllm.py resume1.pdf resume2.pdf resume3.pdf

# Build a searchable resume database and rank with the hybrid approach
python match_embeddings.py add resume1.pdf resume2.pdf resume3.pdf
python match_embeddings.py search
python match_embeddings.py hybrid
```

---

## AI Components

| Module | Model | Purpose |
|---|---|---|
| `resume_parser.py` | `gpt-4o-mini` | Structured field extraction via Pydantic |
| `matchllm.py` | `gpt-4o-mini` | Candidate scoring with sub-scores and reasoning |
| `resume_rewriter.py` | `gpt-4o-mini` | Resume rewriting for a target role |
| `normalizer.py` | `gpt-4o-mini` + local table | Canonical skill, title, and institution names |
| `match_embeddings.py` | `text-embedding-3-small` | Cosine similarity ranking + hybrid pipeline |

Full details in [ai_usage.md](ai_usage.md).

---

## Dependencies

| Library | Purpose |
|---|---|
| `openai` | API client for LLM and embedding calls |
| `pydantic` | Schema enforcement for structured outputs |
| `pypdf` | PDF text extraction |
| `python-docx` | DOCX text extraction |
| `striprtf` | RTF text extraction |
| `beautifulsoup4` | HTML text extraction |
| `numpy` | Cosine similarity for embeddings |
| `flask` | Web interface |
| `python-dotenv` | API key management |

---

## Cost

At experimental scale (a few hundred resumes):
- Resume parsing: ~$0.01–$0.02 per resume
- LLM matching: ~$0.01–$0.03 per comparison
- Embedding: ~$0.02 per million tokens (~$0.001 per resume)
- **Hybrid approach total:** under $10 for a few hundred candidates

---

## Limitations

- **No ground-truth validation** — scores produce plausible output but haven't been measured against labeled hiring data
- **Non-standard formats** — accuracy degrades on image-based PDFs, two-column layouts, and graphically designed resumes (silent failure: wrong data that looks right)
- **Terminology mismatch** — embedding similarity can rank qualified candidates low if they use different terms than the job description
- **Model drift** — no monitoring for behavior changes after OpenAI model updates
- **Not production-ready** — a working prototype is separated from a production tool by reliability, compliance, auditability, and integration work

---

## Project Proposal

Full motivation, design rationale, stretch goals, and honest unknowns: [proposal.md](proposal.md)
