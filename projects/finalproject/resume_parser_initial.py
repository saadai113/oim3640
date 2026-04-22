"""
Resume parser: extracts structured fields from a PDF or DOCX resume using
the OpenAI API with structured outputs.

Usage:
    from resume_parser import parse_resume
    resume_json = parse_resume("path/to/resume.pdf")
"""

import json
import os
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel, Field

# Requires: pip install openai pydantic pypdf python-docx
# Set OPENAI_API_KEY in your environment before running.

# ---------- Pydantic schema for structured output ----------
# Using Pydantic lets OpenAI's structured outputs feature enforce the schema,
# so the model cannot return malformed JSON or invented fields.

class WorkExperience(BaseModel):
    company: str
    title: str
    start_date: str = Field(description="Format: YYYY-MM or YYYY, or 'Unknown'")
    end_date: str = Field(description="Format: YYYY-MM, YYYY, 'Present', or 'Unknown'")
    description: str = Field(description="Responsibilities and achievements")

class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    graduation_year: str = Field(description="YYYY or 'Unknown'")

class ParsedResume(BaseModel):
    name: str
    email: str
    phone: str
    location: str = Field(description="City, state/country, or 'Unknown'")
    summary: str = Field(description="Professional summary or objective if present, else empty string")
    work_experience: list[WorkExperience]
    education: list[Education]
    skills: list[str]
    years_of_experience: float = Field(description="Estimated total years of professional experience")


# ---------- Text extraction from files ----------

def extract_text_from_pdf(path: str) -> str:
    """Extract raw text from a PDF. Returns empty string on failure."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        print(f"PDF extraction failed for {path}: {e}")
        return ""

def extract_text_from_docx(path: str) -> str:
    """Extract raw text from a DOCX file. Returns empty string on failure."""
    try:
        from docx import Document
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        print(f"DOCX extraction failed for {path}: {e}")
        return ""

def extract_text(path: str) -> str:
    """Dispatch to the right extractor based on file extension."""
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    elif suffix in (".docx", ".doc"):
        return extract_text_from_docx(path)
    elif suffix == ".txt":
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


# ---------- Main parsing function ----------

def parse_resume(path: str, model: str = "gpt-4o-mini", api_key: str = None) -> dict:
    """
    Parse a resume file and return structured fields as a dict.
    Returns None if text extraction fails.
    """
    client = OpenAI(api_key=api_key)
    raw_text = extract_text(path)
    if not raw_text.strip():
        print(f"No text extracted from {path}")
        return None

    # Truncate extremely long resumes to stay within reasonable token limits.
    # A typical resume is 2-4 pages (~2000-4000 tokens); 20000 chars is a safe ceiling.
    if len(raw_text) > 20000:
        raw_text = raw_text[:20000]

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You extract structured information from resumes. "
                    "If a field is not present in the resume, use 'Unknown' for strings "
                    "or an empty list for lists. Do not invent information. "
                    "For years_of_experience, estimate based on the work history."
                ),
            },
            {"role": "user", "content": f"Parse this resume:\n\n{raw_text}"},
        ],
        response_format=ParsedResume,
    )

    parsed = completion.choices[0].message.parsed
    return parsed.model_dump() if parsed else None


if __name__ == "__main__":
    # Quick test
    import sys
    if len(sys.argv) < 2:
        print("Usage: python resume_parser.py <path_to_resume>")
        sys.exit(1)

    result = parse_resume(sys.argv[1])
    print(json.dumps(result, indent=2))