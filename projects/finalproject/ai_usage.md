# AI Usage

This project uses the OpenAI API for four distinct AI-powered tasks.

---

## 1. Resume Parsing (`resume_parser.py`)

**Model:** `gpt-4o-mini`  
**Method:** Structured outputs via Pydantic (`client.beta.chat.completions.parse`)

Raw text is extracted from uploaded resume files (PDF, DOCX, RTF, HTML, TXT) and sent to the LLM, which returns a validated JSON object. The schema is enforced by a Pydantic model (`ParsedResume`), so the model cannot return malformed or invented fields.

**Output fields:** name, email, phone, location, summary, work_experience (company, title, dates, description), education (institution, degree, field, graduation year), skills, years_of_experience.

**System prompt role:** Instructs the model to extract only what is present in the resume and use `"Unknown"` for missing fields — no fabrication.

---

## 2. Resume–Job Matching (`matchllm.py`)

**Model:** `gpt-4o-mini`  
**Method:** Structured outputs via Pydantic (`MatchResult`)

The parsed resume (as JSON) and the job description are sent to the LLM, which scores the candidate across four dimensions and provides reasoning.

**Output fields:**
- `overall_score` (0–100)
- `skills_match` (0–100)
- `experience_match` (0–100)
- `education_match` (0–100)
- `strengths` — specific reasons the candidate fits
- `gaps` — specific gaps or concerns
- `summary` — 2–3 sentence overall assessment

**System prompt role:** Instructs the model to act as a technical recruiter, base scores only on evidence in the resume, not inflate scores, and reserve 90+ for exceptional alignment.

---

## 3. Resume Rewriting (`resume_rewriter.py`)

**Model:** `gpt-4o-mini`  
**Method:** Structured outputs via Pydantic (`RewrittenResume`)

The parsed resume and a target job description are sent to the LLM, which rewrites the resume content to better match the role. The model is explicitly constrained from fabricating any experience, credentials, or numbers.

**Output fields:** name, email, phone, location, rewritten summary, work_experience with tailored bullet points, education, skills (reordered by relevance), keywords_added (job description terms that were naturally incorporated).

**System prompt constraints:**
1. Do not fabricate experience, skills, or credentials — only reword existing content.
2. Use strong action verbs (led, built, optimized, reduced, increased).
3. Incorporate job description keywords only where truthfully applicable.
4. Reorder skills to put the most relevant ones first.
5. Rewrite the summary to directly address the specific role.
6. Keep bullets concise — one achievement or responsibility per line.
7. Never invent numbers, outcomes, or titles.

---

## 4. Data Normalization (`normalizer.py`)

**Model:** `gpt-4o-mini` (used for job titles and institution names only)  
**Method:** Standard chat completion (`client.chat.completions.create`, `temperature=0`)

An optional post-processing step that maps extracted fields to canonical forms. Skills are normalized using a local lookup table (no API call). Job titles and institution names are normalized via LLM because the variant space is too large to enumerate in a table.

**Three normalizers:**
- **Skills** (local table, free): `"Python3"` / `"python 3.x"` → `"Python"`, `"k8s"` → `"Kubernetes"`, `"sklearn"` → `"scikit-learn"`. Covers ~200 common tech skills. Unknown skills pass through with basic cleaning.
- **Job titles** (LLM): `"Sr. SWE"` → `"Senior Software Engineer"`, `"SWE III"` → `"Senior Software Engineer"`, `"Jr. Backend Dev"` → `"Junior Backend Developer"`.
- **Institutions** (LLM): `"MIT"` → `"Massachusetts Institute of Technology"`, `"M.I.T."` → same, `"Berkeley"` → `"University of California, Berkeley"`.

Normalization is a separate opt-in step (`parse_resume(..., normalize=True)`) and is not used in the default web application flow.

---

## 5. Embedding-Based Matching (`match_embeddings.py`)

**Model:** `text-embedding-3-small`  
**Method:** `client.embeddings.create`

An alternative (non-default) matching approach that converts resumes and job descriptions into 1536-dimensional vector embeddings and ranks candidates by cosine similarity. Also implements a hybrid approach: embeddings for a cheap first-pass over many candidates, then LLM scoring (from `matchllm.py`) on the top-K shortlist.

This module is not wired into the web app by default but is available for high-volume use cases where calling the LLM for every resume would be cost-prohibitive.

---

## Tools and Libraries

| Library | Purpose |
|---|---|
| `openai` | API client for all LLM and embedding calls |
| `pydantic` | Schema enforcement for structured outputs |
| `pypdf` | PDF text extraction |
| `python-docx` | DOCX text extraction |
| `striprtf` | RTF text extraction |
| `beautifulsoup4` | HTML text extraction |
| `numpy` | Cosine similarity computation for embeddings |

---

## AI Assistance in Development

Claude (claude-sonnet-4-6) was used during development to:
- Design the overall application architecture (Flask backend, React frontend)
- Write and iterate on the system prompts for the parser, matcher, and rewriter
- Build the `resume_rewriter.py` module and `RewrittenResume` Pydantic schema
- Build the Flask API endpoints in `app.py`
- Design the frontend UI in `templates/index.html`
- Debug deployment issues and Jinja2/JSX template conflicts
