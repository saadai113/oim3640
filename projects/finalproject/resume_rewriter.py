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
    Rewrite content in a parsed resume to better match a job description.
    Preserves the original data structure and format.
    Returns the resume_data with updated content, or None on failure.
    """
    resume_json = json.dumps(resume_data, indent=2)

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert resume writer and career coach. Enhance the resume content "
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
                    "Rewrite this resume to better target the job description. "
                    "Return the same structure with improved content."
                ),
            },
        ],
        response_format=RewrittenResume,
    )

    if not completion.choices[0].message.parsed:
        return None

    rewritten = completion.choices[0].message.parsed.model_dump()

    # Merge rewritten content back into original structure to preserve formatting
    if "contact" in resume_data:
        resume_data["contact"]["name"] = rewritten.get("name", resume_data["contact"].get("name"))
        resume_data["contact"]["email"] = rewritten.get("email", resume_data["contact"].get("email"))
        resume_data["contact"]["phone"] = rewritten.get("phone", resume_data["contact"].get("phone"))
        resume_data["contact"]["location"] = rewritten.get("location", resume_data["contact"].get("location"))

    if "summary" in resume_data and "summary" in rewritten:
        resume_data["summary"] = rewritten["summary"]

    # Update work experience while preserving structure
    if "work_experience" in resume_data and "work_experience" in rewritten:
        rewritten_exp_map = {exp["company"]: exp for exp in rewritten["work_experience"]}
        for exp in resume_data["work_experience"]:
            company = exp.get("company", "")
            if company in rewritten_exp_map:
                rewritten_exp = rewritten_exp_map[company]
                exp["title"] = rewritten_exp.get("title", exp.get("title"))
                exp["dates"] = rewritten_exp.get("dates", exp.get("dates"))
                exp["bullets"] = rewritten_exp.get("bullets", exp.get("bullets", []))

    # Update skills while preserving structure
    if "skills" in resume_data and "skills" in rewritten:
        resume_data["skills"] = rewritten["skills"]

    # Update education while preserving structure
    if "education" in resume_data and "education" in rewritten:
        resume_data["education"] = rewritten["education"]

    return resume_data