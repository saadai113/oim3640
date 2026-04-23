"""
Resume rewriter: rewrites and reformats a parsed resume to better match a job description.
Rewrites bullet points, summary, and skill ordering using existing resume content only —
it does not fabricate experience, titles, or credentials.
"""

import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI()


class RewrittenExperience(BaseModel):
    company: str
    title: str
    dates: str
    bullets: list[str] = Field(
        description="3-5 tailored bullet points using strong action verbs and keywords from the job description"
    )


class RewrittenResume(BaseModel):
    name: str
    email: str
    phone: str
    location: str
    summary: str = Field(
        description="3-4 sentence professional summary tailored directly to the specific job"
    )
    work_experience: list[RewrittenExperience]
    education: list[str] = Field(description="Education entries as formatted strings")
    skills: list[str] = Field(
        description="Skills reordered with most relevant to this job first"
    )
    keywords_added: list[str] = Field(
        description="Key terms from the job description that were naturally incorporated"
    )


def rewrite_resume(resume_data: dict, job_description: str, model: str = "gpt-4o-mini") -> dict | None:
    """
    Rewrite and reformat a parsed resume to better match a job description.
    Returns a dict with rewritten sections, or None on failure.
    """
    resume_json = json.dumps(resume_data, indent=2)

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert resume writer and career coach. Rewrite the resume "
                    "to better match the job description. Rules:\n"
                    "1. Do NOT fabricate experience, skills, or credentials — only reword existing content.\n"
                    "2. Use strong action verbs (led, built, optimized, reduced, increased, etc.).\n"
                    "3. Naturally incorporate keywords from the job description where truthfully applicable.\n"
                    "4. Reorder skills to put the most job-relevant ones first.\n"
                    "5. Rewrite the summary to directly address this specific role and company type.\n"
                    "6. Keep bullets concise — one strong achievement or responsibility per line.\n"
                    "7. Maintain factual accuracy — never invent numbers, outcomes, or titles."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"JOB DESCRIPTION:\n{job_description}\n\n"
                    f"ORIGINAL RESUME (parsed):\n{resume_json}\n\n"
                    "Rewrite this resume to better target the job description."
                ),
            },
        ],
        response_format=RewrittenResume,
    )

    result = completion.choices[0].message.parsed
    return result.model_dump() if result else None
