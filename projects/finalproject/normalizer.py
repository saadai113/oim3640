"""
Data normalization for parsed resumes.

Maps raw extracted fields to canonical forms so that matching and search
work on consistent representations rather than surface-level strings.

Three normalizers:
    1. Skills: "Python3" / "python" / "Python 3.x" -> "Python"
    2. Job titles: "Sr. Software Eng." / "SWE III" -> "Senior Software Engineer"
    3. Institutions: "MIT" / "M.I.T." -> "Massachusetts Institute of Technology"

Design decisions:
    - Skills use a local lookup table (fast, no API cost, deterministic).
      The table covers the ~200 most common tech skills. Unknown skills
      pass through unchanged.
    - Job titles and institutions use an LLM call (too many variants to
      enumerate in a table). This adds ~$0.005 per resume but handles
      arbitrary inputs.
    - Normalization is a separate post-processing step, not baked into the
      parser. This keeps the parser's output faithful to what the resume
      actually says, with normalization as an explicit transformation you
      can inspect, disable, or swap out.

Usage:
    from normalizer import normalize_resume
    raw = parse_resume("resume.pdf")
    normalized = normalize_resume(raw)

    # Or normalize individual fields:
    from normalizer import normalize_skills, normalize_title, normalize_institution
    canonical_skills = normalize_skills(["Python3", "JS", "k8s"])
    canonical_title = normalize_title("Sr. SWE")
"""

import json
import re
from openai import OpenAI

client = OpenAI()


# ---------- Skills normalization (local lookup, no API cost) ----------

# Mapping of common variants to canonical form.
# Lowercase keys. If a skill isn't in this table, it passes through with
# only basic cleaning (strip whitespace, title case).
# This covers the most frequent collision cases. Extend as needed.

SKILLS_MAP = {
    # Python
    "python": "Python", "python3": "Python", "python 3": "Python",
    "python3.x": "Python", "python 3.x": "Python", "python 3.10": "Python",
    "python 3.11": "Python", "python 3.12": "Python", "python2": "Python",
    "python 2": "Python",

    # JavaScript ecosystem
    "javascript": "JavaScript", "js": "JavaScript", "es6": "JavaScript",
    "ecmascript": "JavaScript", "typescript": "TypeScript", "ts": "TypeScript",
    "node": "Node.js", "nodejs": "Node.js", "node.js": "Node.js",
    "react": "React", "reactjs": "React", "react.js": "React",
    "vue": "Vue.js", "vuejs": "Vue.js", "vue.js": "Vue.js",
    "angular": "Angular", "angularjs": "Angular",
    "next": "Next.js", "nextjs": "Next.js", "next.js": "Next.js",
    "express": "Express.js", "expressjs": "Express.js",

    # Java / JVM
    "java": "Java", "kotlin": "Kotlin", "scala": "Scala",
    "spring": "Spring", "spring boot": "Spring Boot", "springboot": "Spring Boot",

    # C family
    "c": "C", "c++": "C++", "cpp": "C++", "c#": "C#", "csharp": "C#",
    ".net": ".NET", "dotnet": ".NET", "asp.net": "ASP.NET",

    # Go / Rust
    "go": "Go", "golang": "Go", "rust": "Rust", "rustlang": "Rust",

    # Ruby / PHP
    "ruby": "Ruby", "rails": "Ruby on Rails", "ruby on rails": "Ruby on Rails",
    "ror": "Ruby on Rails", "php": "PHP", "laravel": "Laravel",

    # Databases
    "sql": "SQL", "mysql": "MySQL", "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL", "psql": "PostgreSQL",
    "mongo": "MongoDB", "mongodb": "MongoDB",
    "redis": "Redis", "elasticsearch": "Elasticsearch", "es": "Elasticsearch",
    "dynamodb": "DynamoDB", "dynamo": "DynamoDB",
    "sqlite": "SQLite", "oracle db": "Oracle Database",
    "oracle": "Oracle Database", "cassandra": "Cassandra",
    "neo4j": "Neo4j", "cockroachdb": "CockroachDB",

    # Cloud
    "aws": "AWS", "amazon web services": "AWS",
    "gcp": "GCP", "google cloud": "GCP", "google cloud platform": "GCP",
    "azure": "Azure", "microsoft azure": "Azure",

    # DevOps / Infra
    "docker": "Docker", "kubernetes": "Kubernetes", "k8s": "Kubernetes",
    "terraform": "Terraform", "ansible": "Ansible", "puppet": "Puppet",
    "chef": "Chef", "jenkins": "Jenkins", "ci/cd": "CI/CD", "cicd": "CI/CD",
    "github actions": "GitHub Actions", "gha": "GitHub Actions",
    "gitlab ci": "GitLab CI", "circleci": "CircleCI",
    "nginx": "NGINX", "apache": "Apache",

    # Data / ML
    "pandas": "pandas", "numpy": "NumPy", "scipy": "SciPy",
    "scikit-learn": "scikit-learn", "sklearn": "scikit-learn",
    "tensorflow": "TensorFlow", "tf": "TensorFlow",
    "pytorch": "PyTorch", "torch": "PyTorch",
    "keras": "Keras", "spark": "Apache Spark", "apache spark": "Apache Spark",
    "pyspark": "PySpark", "hadoop": "Hadoop", "hive": "Hive",
    "airflow": "Apache Airflow", "apache airflow": "Apache Airflow",
    "kafka": "Apache Kafka", "apache kafka": "Apache Kafka",
    "rabbitmq": "RabbitMQ", "rabbit mq": "RabbitMQ",
    "dbt": "dbt", "snowflake": "Snowflake", "bigquery": "BigQuery",
    "redshift": "Redshift", "databricks": "Databricks",
    "mlflow": "MLflow", "huggingface": "Hugging Face",
    "hugging face": "Hugging Face", "langchain": "LangChain",
    "openai": "OpenAI API", "openai api": "OpenAI API",

    # Web / API
    "rest": "REST APIs", "rest api": "REST APIs", "rest apis": "REST APIs",
    "restful": "REST APIs", "graphql": "GraphQL",
    "grpc": "gRPC", "websocket": "WebSockets", "websockets": "WebSockets",
    "fastapi": "FastAPI", "flask": "Flask", "django": "Django",

    # Version control
    "git": "Git", "github": "GitHub", "gitlab": "GitLab",
    "bitbucket": "Bitbucket", "svn": "SVN", "subversion": "SVN",

    # Misc tools
    "jira": "Jira", "confluence": "Confluence", "slack": "Slack",
    "figma": "Figma", "postman": "Postman", "swagger": "Swagger",
    "linux": "Linux", "unix": "Unix", "bash": "Bash",
    "powershell": "PowerShell", "shell scripting": "Shell Scripting",
    "agile": "Agile", "scrum": "Scrum", "kanban": "Kanban",

    # Data formats / protocols
    "json": "JSON", "xml": "XML", "csv": "CSV", "yaml": "YAML",
    "protobuf": "Protocol Buffers", "protocol buffers": "Protocol Buffers",

    # Testing
    "pytest": "pytest", "junit": "JUnit", "jest": "Jest",
    "selenium": "Selenium", "cypress": "Cypress",
    "unit testing": "Unit Testing", "tdd": "TDD",

    # Security / Compliance
    "oauth": "OAuth", "oauth2": "OAuth 2.0", "oauth 2.0": "OAuth 2.0",
    "jwt": "JWT", "ssl": "SSL/TLS", "tls": "SSL/TLS",
    "pci-dss": "PCI-DSS", "pci dss": "PCI-DSS",
    "soc 2": "SOC 2", "soc2": "SOC 2", "gdpr": "GDPR", "hipaa": "HIPAA",
}


def normalize_skills(skills: list[str]) -> list[str]:
    """
    Map a list of raw skill strings to canonical forms.
    Uses local lookup table—no API cost, deterministic, fast.
    Unknown skills pass through with basic cleaning (strip, title case).
    Deduplicates after normalization.
    """
    normalized = []
    seen = set()
    for skill in skills:
        key = skill.strip().lower()
        # Remove trailing periods, commas, semicolons
        key = re.sub(r'[.,;:]+$', '', key).strip()

        canonical = SKILLS_MAP.get(key, None)
        if canonical is None:
            # Not in lookup table—apply basic cleaning only
            # Title case, but preserve known acronyms
            canonical = skill.strip()
            if canonical.upper() == canonical and len(canonical) <= 5:
                pass  # Likely an acronym (AWS, SQL, etc.), leave as-is
            elif canonical.lower() == canonical:
                canonical = canonical.title()

        if canonical.lower() not in seen:
            seen.add(canonical.lower())
            normalized.append(canonical)

    return normalized


# ---------- Job title normalization (LLM-based) ----------

def normalize_titles(titles: list[str], model: str = "gpt-4o-mini") -> dict[str, str]:
    """
    Map a list of raw job titles to canonical forms using an LLM.
    Returns a dict of {original: canonical}.

    Batches all titles in a single call to minimize cost.
    Typical cost: ~$0.005 per resume.
    """
    if not titles:
        return {}

    prompt = (
        "Normalize these job titles to standard industry forms. Rules:\n"
        "- Expand abbreviations: 'Sr.' -> 'Senior', 'Jr.' -> 'Junior', "
        "'Eng.' -> 'Engineer', 'Mgr' -> 'Manager', 'VP' -> 'Vice President'\n"
        "- Map level codes to words: 'SWE III' -> 'Senior Software Engineer', "
        "'L5' -> 'Senior', 'IC4' -> 'Senior'\n"
        "- Standardize variants: 'Dev' -> 'Developer', 'Prog' -> 'Programmer'\n"
        "- Keep the functional area: 'Sr. BE' -> 'Senior Backend Engineer'\n"
        "- If a title is already standard, return it unchanged\n"
        "- If a title is ambiguous, make your best guess\n\n"
        "Return ONLY a JSON object mapping each input title to its normalized form. "
        "No other text.\n\n"
        "Input titles:\n"
    )
    for t in titles:
        prompt += f"- {t}\n"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        return json.loads(raw)
    except Exception as e:
        print(f"Title normalization failed: {e}")
        return {t: t for t in titles}


# ---------- Institution normalization (LLM-based) ----------

def normalize_institutions(institutions: list[str], model: str = "gpt-4o-mini") -> dict[str, str]:
    """
    Map a list of raw institution names to canonical forms using an LLM.
    Returns a dict of {original: canonical}.

    Handles abbreviations (MIT, CMU, UCLA), punctuation variants (M.I.T.),
    partial names (Berkeley vs UC Berkeley), and international institutions.
    """
    if not institutions:
        return {}

    prompt = (
        "Normalize these educational institution names to their full, official forms. Rules:\n"
        "- Expand common abbreviations: 'MIT' -> 'Massachusetts Institute of Technology', "
        "'CMU' -> 'Carnegie Mellon University', 'UCLA' -> "
        "'University of California, Los Angeles'\n"
        "- Resolve ambiguous short names: 'Berkeley' -> 'University of California, Berkeley'\n"
        "- Remove punctuation variants: 'M.I.T.' -> 'Massachusetts Institute of Technology'\n"
        "- Keep already-full names unchanged\n"
        "- For institutions you don't recognize, return them unchanged\n\n"
        "Return ONLY a JSON object mapping each input name to its normalized form. "
        "No other text.\n\n"
        "Input institutions:\n"
    )
    for i in institutions:
        prompt += f"- {i}\n"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        return json.loads(raw)
    except Exception as e:
        print(f"Institution normalization failed: {e}")
        return {i: i for i in institutions}


# ---------- Full resume normalization ----------

def normalize_resume(resume: dict, model: str = "gpt-4o-mini") -> dict:
    """
    Apply all normalization steps to a parsed resume dict.
    Returns a new dict with normalized fields. The original is not modified.

    Adds a 'normalization' key to the output with metadata about what changed,
    so you can inspect the mapping and verify correctness.
    """
    import copy
    r = copy.deepcopy(resume)

    changes = {}

    # 1. Normalize skills (local lookup, free)
    raw_skills = r.get("skills", [])
    r["skills"] = normalize_skills(raw_skills)
    skill_changes = {
        orig: norm for orig, norm in zip(raw_skills, r["skills"])
        if orig != norm
    }
    # The above zip comparison doesn't work perfectly since normalize_skills
    # deduplicates—track changes differently
    if set(raw_skills) != set(r["skills"]):
        changes["skills"] = {
            "before_count": len(raw_skills),
            "after_count": len(r["skills"]),
            "deduplicated": len(raw_skills) - len(r["skills"]),
        }

    # 2. Normalize job titles (LLM call)
    raw_titles = [job.get("title", "") for job in r.get("work_experience", [])]
    if raw_titles:
        title_map = normalize_titles(raw_titles, model=model)
        title_changes = {}
        for job in r["work_experience"]:
            original = job.get("title", "")
            normalized = title_map.get(original, original)
            if original != normalized:
                title_changes[original] = normalized
            job["title"] = normalized
        if title_changes:
            changes["titles"] = title_changes

    # 3. Normalize institutions (LLM call)
    raw_institutions = [
        edu.get("institution", "")
        for edu in r.get("education", [])
    ]
    if raw_institutions:
        inst_map = normalize_institutions(raw_institutions, model=model)
        inst_changes = {}
        for edu in r["education"]:
            original = edu.get("institution", "")
            normalized = inst_map.get(original, original)
            if original != normalized:
                inst_changes[original] = normalized
            edu["institution"] = normalized
        if inst_changes:
            changes["institutions"] = inst_changes

    # Attach normalization metadata
    r["_normalization"] = {
        "applied": True,
        "changes": changes,
        "fields_normalized": ["skills", "work_experience[].title", "education[].institution"],
    }

    return r


if __name__ == "__main__":
    # Demo with sample data
    sample = {
        "name": "Test Candidate",
        "email": "test@email.com",
        "phone": "555-0100",
        "location": "San Francisco, CA",
        "summary": "Experienced software engineer.",
        "work_experience": [
            {
                "company": "Stripe",
                "title": "Sr. SWE",
                "start_date": "2021-01",
                "end_date": "Present",
                "description": "Built payment systems.",
            },
            {
                "company": "Google",
                "title": "SWE III",
                "start_date": "2018-06",
                "end_date": "2020-12",
                "description": "Worked on search infrastructure.",
            },
            {
                "company": "Startup Inc",
                "title": "Jr. Backend Dev",
                "start_date": "2016-08",
                "end_date": "2018-05",
                "description": "Built APIs.",
            },
        ],
        "education": [
            {
                "institution": "MIT",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "graduation_year": "2016",
            }
        ],
        "skills": [
            "Python3", "JS", "k8s", "postgres", "aws",
            "Amazon Web Services", "react.js", "REST API",
            "Docker", "terraform", "sklearn",
        ],
        "years_of_experience": 7.0,
    }

    print("BEFORE NORMALIZATION:")
    print(f"  Skills: {sample['skills']}")
    print(f"  Titles: {[j['title'] for j in sample['work_experience']]}")
    print(f"  Institutions: {[e['institution'] for e in sample['education']]}")

    normalized = normalize_resume(sample)

    print("\nAFTER NORMALIZATION:")
    print(f"  Skills: {normalized['skills']}")
    print(f"  Titles: {[j['title'] for j in normalized['work_experience']]}")
    print(f"  Institutions: {[e['institution'] for e in normalized['education']]}")

    print("\nCHANGES:")
    print(json.dumps(normalized["_normalization"], indent=2))