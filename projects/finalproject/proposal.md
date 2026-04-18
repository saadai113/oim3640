# LLM-Powered Resume Parsing and Candidate-Job Matching System

**Author:** Saad  
**Institution:** Babson College  
**Date:** April 2026

---

## What I'm Building

A Python pipeline that takes a stack of resumes (PDF, DOCX, or plaintext), extracts structured data from each one using an LLM, and ranks them against a given job description. The system has three modules:

`resume_parser.py` handles file intake. It pulls raw text from a resume using `pypdf` or `python-docx`, sends it to OpenAI's GPT-4o-mini with a Pydantic-enforced JSON schema, and gets back a clean, typed data structure: name, contact info, work experience (company, title, dates, description), education, skills, and estimated years of experience. The structured outputs feature guarantees the model returns valid JSON conforming to the schema every time—no post-hoc parsing or validation layer needed.

`match_llm.py` is the simple matching approach. It sends a parsed resume plus a job description to the LLM and gets back a structured evaluation: overall score (0–100), sub-scores for skills, experience, and education, specific strengths, specific gaps, and a narrative summary. The system prompt is calibrated to resist the score-inflation tendency LLMs have in evaluative tasks—70 means "solid fit with gaps," 90+ is rare. Every comparison costs one LLM call (~$0.01–$0.03), so this scales linearly with candidate count.

`match_embeddings.py` is the scalable matching approach. It converts each parsed resume into a vector embedding (OpenAI's `text-embedding-3-small`, ~$0.02 per million tokens), stores the embeddings in a local database, and uses cosine similarity to do a cheap first-pass ranking when a job description comes in. Only the top-K candidates from the embedding pass get sent to the LLM for detailed scoring. This cuts LLM costs by 90–95% compared to scoring every resume. The database is pickle-based, which works up to roughly 10,000 resumes before needing migration to a vector DB (pgvector, Qdrant).

A key design choice throughout: embeddings are computed on a clean text representation reconstructed from the parsed JSON, not on the raw extracted PDF text. Raw extraction output is full of formatting noise—page numbers, header repetitions, column artifacts—that degrades embedding quality. Cleaning it first produces noticeably better ranking consistency.

## Why

The immediate motivation is practical: recruiters spend 6–8 seconds per resume during initial screening, which makes the process both inconsistent and biased toward superficial signals (school name, employer brand, formatting quality). Traditional resume parsers (rules-based NER, regex) have existed for a decade but break on anything non-standard: creative layouts, inconsistent date formats, varied skill terminology, international conventions.

The deeper motivation is to demonstrate a specific technical thesis: that modern LLM APIs have shifted the work in applied NLP from model engineering to system design. This project requires no custom training, no GPU infrastructure, no specialized NLP libraries. The entire system runs on a laptop with five pip-installable dependencies and an API key. The analytical work is in schema design, prompt calibration, cost optimization, and pipeline architecture—not in building or fine-tuning models. That shift is underappreciated, and the project is intended to make it concrete.

From a portfolio perspective, the project demonstrates: treating LLMs as typed infrastructure (Pydantic schemas, structured outputs) rather than conversational tools; reasoning about cost-performance tradeoffs at the systems level (the hybrid architecture exists because the naive approach doesn't scale economically); and honest assessment of what works and what doesn't, which is harder to show than technical proficiency but arguably more valuable.

## MVP (What Exists Now)

The MVP is functional. It can:

- Accept a PDF, DOCX, or plaintext resume and extract structured fields with high accuracy on well-formatted inputs. The Pydantic schema enforces output structure, so malformed responses don't reach downstream logic.

- Score a single resume against a single job description with sub-scores, strengths, gaps, and a narrative summary. The prompt anchoring keeps scores in a usable distribution rather than clustering everything at 80+.

- Ingest multiple resumes into a persistent embedding database, rank them by cosine similarity against a job description, and run detailed LLM scoring on only the top candidates (hybrid approach).

- Run end-to-end from the command line: `python match_embeddings.py add *.pdf`, then `python match_embeddings.py hybrid`.

The total dependency footprint is five packages: `openai`, `pydantic`, `pypdf`, `python-docx`, `numpy`. Cost at experimental scale (a few hundred resumes) is under $10 in API fees.

## Stretch Goals (What Could Come Next)

**OCR integration for image-based PDFs.** The single biggest extraction failure mode is resumes that are images rather than text (scanned documents, Canva exports, heavily designed layouts). Adding Tesseract or a cloud OCR layer before the LLM call would expand the range of processable inputs significantly. Straightforward to implement but adds a dependency and a latency step.

**Extraction confidence scoring.** Currently the system fails silently on bad inputs—garbled text gets sent to the LLM, which produces plausible-looking but wrong output. A confidence score on the extraction step (based on text density, character distribution, structural markers) would let the system flag resumes that probably parsed badly and route them to manual review.

**Web interface.** The current system is command-line only. A minimal Flask or Streamlit frontend that lets a user upload resumes, paste a job description, and see ranked results would make the project demonstrable to non-technical evaluators. This is cosmetic rather than analytical work, but it matters for portfolio presentation.

**Multi-job matching.** The current architecture scores resumes against one job at a time. A natural extension is to ingest a set of open roles, embed all of them, and for each incoming resume, identify which roles it best fits. The embedding infrastructure already supports this—it requires inverting the query direction but no new architecture.

**Validated evaluation against a test set.** Build a labeled dataset of resume-job pairs with human-assigned match quality scores, and measure precision, recall, and rank correlation against the system's output. This is the most important stretch goal because without it, the system's output quality is anecdotal rather than measured. It's also the most time-intensive—creating reliable ground-truth labels for hiring fit is genuinely hard, which is why most tools in this category don't publish benchmarks.

**Temperature-zero deterministic mode.** Setting temperature to zero and implementing response caching so that the same resume scored twice against the same job always returns identical results. Important for any application where score reproducibility matters (audit trails, compliance, A/B testing of prompt changes).

## What I Don't Know Yet

**Whether the scores are actually meaningful.** The system produces plausible-looking output—scores, strengths, gaps, summaries—but I have no ground-truth labels to validate against. Without a labeled test set of "correct" matches, there is no way to compute precision, recall, or measure whether the rankings correlate with actual hiring outcomes. The scores could be directionally useful or they could be sophisticated-looking noise. I don't know which, and building the validation dataset to find out is a significant project in itself.

**How much extraction accuracy degrades on non-standard resumes.** I've tested on well-formatted, text-based PDFs. I don't have systematic data on failure rates across the long tail of resume formats: two-column layouts, graphically designed resumes, international conventions (photos, birth dates, marital status common in European and Asian resumes), resumes in languages other than English. The failure mode is not obvious—the system doesn't crash; it returns wrong data that looks right.

**Whether embedding similarity is a good enough first-pass filter.** The hybrid approach assumes that cosine similarity between resume and job description embeddings is a reasonable proxy for candidate relevance—good enough to narrow from 1,000 to 20 candidates without losing qualified people in the cut. This assumption hasn't been tested rigorously. A resume that uses different terminology than the job description for equivalent skills could rank low in embeddings despite being a strong match. I don't know how often this happens in practice.

**How score consistency varies across model versions.** OpenAI periodically updates the models behind their API endpoints. A prompt that produces well-calibrated scores on today's GPT-4o-mini may behave differently after a model update. I don't have a monitoring or regression-testing setup to detect this. For a one-time portfolio project this is acceptable; for anything resembling production use it's a gap.

**What the real cost curve looks like at scale.** The cost analysis in this proposal is based on published API pricing and estimated token counts. Actual costs depend on resume length distribution, how verbose the model is in its responses, retry rates on failed calls, and whether OpenAI changes pricing. I have estimates, not measurements.

**Whether this solves a problem anyone would pay for.** Commercial resume parsing and matching is a real market (Sovren, RChilli, Textkernel, HireAbility charge $0.10–$0.50 per parse). But those companies have spent years handling edge cases, building compliance features, and earning enterprise trust. A working prototype and a viable product are separated by a large gap in reliability, security, auditability, and integration work. I don't know whether the LLM-native approach has structural advantages large enough to close that gap, or whether it's a more elegant way to reach roughly the same accuracy ceiling.

## Repository Structure

```
resume_parser.py        # Text extraction and structured field parsing
match_llm.py            # Direct LLM-based candidate-job matching
match_embeddings.py     # Embedding similarity + hybrid ranking pipeline
```

## Dependencies and Setup

```
pip install openai pydantic pypdf python-docx numpy
export OPENAI_API_KEY=<your-key>
```

## Usage

```bash
# Parse a single resume
python resume_parser.py resume.pdf

# Rank candidates against a job description (LLM-only)
python match_llm.py resume1.pdf resume2.pdf resume3.pdf

# Build a searchable resume database and rank with hybrid approach
python match_embeddings.py add resume1.pdf resume2.pdf resume3.pdf
python match_embeddings.py search
python match_embeddings.py hybrid
```