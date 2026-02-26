import re
import spacy
from dataclasses import dataclass, field

nlp = spacy.load("en_core_web_sm")

SKILL_KEYWORDS = [
    "Python", "FastAPI", "Django", "Flask", "React", "Vue", "Angular",
    "Docker", "Kubernetes", "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "JavaScript", "TypeScript", "Node.js", "Java", "C++", "C#", "Go", "Rust",
    "AWS", "Azure", "GCP", "Linux", "Git", "REST", "GraphQL", "Kafka", "Spark",
    "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn", "Airflow",
    "Terraform", "Ansible", "Jenkins", "GitHub Actions", "CI/CD", "Agile",
    "Scrum", "Microservices", "DevOps", "Machine Learning", "Deep Learning",
    "NLP", "Computer Vision", "Data Science", "Data Engineering", "Swift",
    "Kotlin", "Flutter", "React Native", "Spring Boot", "Hibernate",
]


@dataclass
class ParsedDocument:
    raw_text: str
    name: str = ""
    email: str = ""
    skills: list[str] = field(default_factory=list)
    total_years_experience: float = 0.0
    job_titles: list[str] = field(default_factory=list)
    city: str = ""
    state: str = ""
    country: str = ""
    education: str = ""
    is_remote_ok: bool = False


# Alias used in tests
ParsedResume = ParsedDocument


def parse_text(text: str) -> ParsedDocument:
    doc = ParsedDocument(raw_text=text)
    doc.email = _extract_email(text)
    doc.name = _extract_name(text)
    doc.skills = _extract_skills(text)
    doc.total_years_experience = _extract_experience_years(text)
    doc.city, doc.state, doc.country = _extract_location(text)
    doc.education = _extract_education(text)
    doc.is_remote_ok = bool(re.search(r"\bremote\b", text, re.IGNORECASE))
    return doc


def _extract_email(text: str) -> str:
    m = re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", text, re.IGNORECASE)
    return m.group(0) if m else ""


def _extract_name(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    # Return first non-email line that looks like a name (1-4 words, capitalised)
    for line in lines[:5]:
        if "@" in line:
            continue
        if re.match(r"^[A-Z][a-z]+(?:\s[A-Z][a-z]+){0,3}$", line):
            return line
    return lines[0] if lines else ""


def _extract_skills(text: str) -> list[str]:
    found = []
    for skill in SKILL_KEYWORDS:
        if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
            found.append(skill)
    return found


def _extract_experience_years(text: str) -> float:
    # Date ranges like (2018 - 2023) or (2020 – Present)
    ranges = re.findall(
        r"(20\d{2}|19\d{2})\s*[-–]\s*(20\d{2}|19\d{2}|present)",
        text,
        re.IGNORECASE,
    )
    if ranges:
        current_year = 2026
        total = 0.0
        for start, end in ranges:
            e = current_year if end.lower() == "present" else int(end)
            total += max(0, e - int(start))
        return round(total, 1)

    # Explicit "X years" mentions
    explicit = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*years?", text, re.IGNORECASE)
    if explicit:
        # Take the max to avoid double-counting
        values = [float(y) for y in explicit]
        return round(max(values), 1)

    return 0.0


def _extract_location(text: str) -> tuple[str, str, str]:
    # Pattern: City, State/Province, Country  e.g. New York, NY, USA
    m = re.search(
        r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*),\s*"
        r"([A-Z]{2}|[A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*"
        r"(USA|UK|India|Canada|Australia|Germany|France|Singapore|[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b",
        text,
    )
    if m:
        return m.group(1), m.group(2), m.group(3)

    # Pattern: City, Country  e.g. London, UK
    m2 = re.search(
        r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*),\s*"
        r"(USA|UK|India|Canada|Australia|Germany|France|Singapore)\b",
        text,
    )
    if m2:
        return m2.group(1), "", m2.group(2)

    return "", "", ""


def _extract_education(text: str) -> str:
    degree_patterns = [
        "B.Sc", "B.S.", "B.E.", "B.Tech", "B.A.",
        "M.Sc", "M.S.", "M.E.", "M.Tech", "MBA",
        "Ph.D", "PhD", "Doctor",
        "Bachelor", "Master",
    ]
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        for deg in degree_patterns:
            if deg.lower() in stripped.lower():
                return stripped
    return ""
