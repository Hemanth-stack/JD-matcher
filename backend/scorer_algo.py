from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from parser import ParsedDocument

WEIGHTS = {
    "skills": 0.40,
    "experience": 0.30,
    "location": 0.20,
    "education": 0.10,
}


@dataclass
class ScoreBreakdown:
    skills_score: float       # 0-100
    experience_score: float   # 0-100
    location_score: float     # 0-100
    education_score: float    # 0-100
    total_score: float        # weighted 0-100


def score_algorithmic(jd: ParsedDocument, resume: ParsedDocument) -> ScoreBreakdown:
    skills = _score_skills(jd, resume)
    exp    = _score_experience(jd, resume)
    loc    = _score_location(jd, resume)
    edu    = _score_education(jd, resume)

    total = (
        skills * WEIGHTS["skills"]
        + exp    * WEIGHTS["experience"]
        + loc    * WEIGHTS["location"]
        + edu    * WEIGHTS["education"]
    )

    return ScoreBreakdown(
        skills_score=round(skills, 1),
        experience_score=round(exp, 1),
        location_score=round(loc, 1),
        education_score=round(edu, 1),
        total_score=round(total, 1),
    )


# ---------------------------------------------------------------------------
# Dimension scorers
# ---------------------------------------------------------------------------

def _score_skills(jd: ParsedDocument, resume: ParsedDocument) -> float:
    if not jd.skills:
        return 100.0

    # Keyword overlap (60% weight within skills dimension)
    jd_set  = {s.lower() for s in jd.skills}
    res_set = {s.lower() for s in resume.skills}
    keyword_score = len(jd_set & res_set) / len(jd_set) * 100.0

    # TF-IDF cosine similarity on raw text (40% weight within skills dimension)
    try:
        vect  = TfidfVectorizer(stop_words="english", min_df=1)
        tfidf = vect.fit_transform([jd.raw_text, resume.raw_text])
        tfidf_score = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]) * 100.0
    except Exception:
        tfidf_score = keyword_score

    return min(100.0, keyword_score * 0.6 + tfidf_score * 0.4)


def _score_experience(jd: ParsedDocument, resume: ParsedDocument) -> float:
    required  = jd.total_years_experience
    if required == 0:
        return 100.0
    candidate = resume.total_years_experience
    if candidate >= required:
        return 100.0
    return round((candidate / required) * 100.0, 1)


def _score_location(jd: ParsedDocument, resume: ParsedDocument) -> float:
    # Remote anywhere → full score
    if jd.is_remote_ok or resume.is_remote_ok:
        return 100.0
    # JD has no location requirement
    if not jd.city and not jd.state and not jd.country:
        return 100.0

    if jd.city and resume.city and jd.city.lower() == resume.city.lower():
        return 100.0
    if jd.state and resume.state and jd.state.lower() == resume.state.lower():
        return 60.0
    if jd.country and resume.country and jd.country.lower() == resume.country.lower():
        return 30.0
    return 0.0


def _score_education(jd: ParsedDocument, resume: ParsedDocument) -> float:
    if not jd.education:
        return 100.0

    degree_map = {
        "phd":      ["ph.d", "phd", "doctor"],
        "master":   ["m.sc", "m.s.", "m.e.", "m.tech", "master", "mba"],
        "bachelor": ["b.sc", "b.s.", "b.e.", "b.tech", "b.a.", "bachelor"],
    }

    jd_edu_lower  = jd.education.lower()
    res_edu_lower = resume.education.lower()

    for _level, keywords in degree_map.items():
        if any(k in jd_edu_lower for k in keywords):
            return 100.0 if any(k in res_edu_lower for k in keywords) else 30.0

    # Generic keyword overlap fallback
    stop = {"of", "in", "the", "and", "for", "a", "an"}
    jd_words  = set(jd.education.lower().split()) - stop
    res_words = set(resume.education.lower().split()) - stop
    if not jd_words:
        return 100.0
    return min(100.0, len(jd_words & res_words) / len(jd_words) * 100.0)
