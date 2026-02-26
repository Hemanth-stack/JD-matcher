from parser import ParsedDocument
from scorer_algo import ScoreBreakdown, score_algorithmic


def make_doc(**kwargs) -> ParsedDocument:
    defaults = dict(
        raw_text="",
        name="",
        email="",
        skills=[],
        total_years_experience=0.0,
        job_titles=[],
        city="",
        state="",
        country="",
        education="",
        is_remote_ok=False,
    )
    defaults.update(kwargs)
    return ParsedDocument(**defaults)


def test_perfect_skills_match():
    # Keyword overlap is 100%, TF-IDF may be < 100 due to differing words,
    # so combined score should be high (>= 60% * 100 = 60) but not necessarily 100.
    jd     = make_doc(skills=["Python", "Docker"], raw_text="Python Docker developer")
    resume = make_doc(skills=["Python", "Docker"], raw_text="Python Docker engineer")
    result = score_algorithmic(jd, resume)
    assert result.skills_score >= 60.0  # at minimum the keyword score portion


def test_zero_skills_match():
    jd     = make_doc(skills=["Java"],   raw_text="Java developer")
    resume = make_doc(skills=["Python"], raw_text="Python engineer")
    result = score_algorithmic(jd, resume)
    assert result.skills_score == 0.0


def test_partial_skills_match():
    jd     = make_doc(skills=["Python", "Docker", "SQL"], raw_text="Python Docker SQL")
    resume = make_doc(skills=["Python"],                  raw_text="Python developer")
    result = score_algorithmic(jd, resume)
    assert 0 < result.skills_score < 100


def test_experience_sufficient():
    jd     = make_doc(total_years_experience=3.0)
    resume = make_doc(total_years_experience=5.0)
    result = score_algorithmic(jd, resume)
    assert result.experience_score == 100.0


def test_experience_insufficient():
    jd     = make_doc(total_years_experience=5.0)
    resume = make_doc(total_years_experience=2.0)
    result = score_algorithmic(jd, resume)
    assert result.experience_score == 40.0


def test_experience_no_requirement():
    jd     = make_doc(total_years_experience=0.0)
    resume = make_doc(total_years_experience=3.0)
    result = score_algorithmic(jd, resume)
    assert result.experience_score == 100.0


def test_location_same_city():
    jd     = make_doc(city="New York", state="NY", country="USA")
    resume = make_doc(city="New York", state="NY", country="USA")
    result = score_algorithmic(jd, resume)
    assert result.location_score == 100.0


def test_location_same_state():
    jd     = make_doc(city="New York", state="NY", country="USA")
    resume = make_doc(city="Buffalo",  state="NY", country="USA")
    result = score_algorithmic(jd, resume)
    assert result.location_score == 60.0


def test_location_same_country():
    jd     = make_doc(city="New York", state="NY", country="USA")
    resume = make_doc(city="Chicago",  state="IL", country="USA")
    result = score_algorithmic(jd, resume)
    assert result.location_score == 30.0


def test_location_remote_jd():
    jd     = make_doc(is_remote_ok=True)
    resume = make_doc(city="Tokyo", country="Japan")
    result = score_algorithmic(jd, resume)
    assert result.location_score == 100.0


def test_location_remote_resume():
    jd     = make_doc(city="London", country="UK")
    resume = make_doc(is_remote_ok=True)
    result = score_algorithmic(jd, resume)
    assert result.location_score == 100.0


def test_education_match():
    jd     = make_doc(education="B.Sc Computer Science")
    resume = make_doc(education="B.Sc Software Engineering")
    result = score_algorithmic(jd, resume)
    assert result.education_score == 100.0


def test_education_degree_mismatch():
    jd     = make_doc(education="Ph.D Machine Learning")
    resume = make_doc(education="B.Sc Computer Science")
    result = score_algorithmic(jd, resume)
    assert result.education_score == 30.0


def test_returns_score_breakdown():
    jd     = make_doc(skills=["Python"], total_years_experience=2, country="USA")
    resume = make_doc(skills=["Python"], total_years_experience=3, country="USA")
    result = score_algorithmic(jd, resume)
    assert isinstance(result, ScoreBreakdown)
    assert 0 <= result.total_score <= 100
