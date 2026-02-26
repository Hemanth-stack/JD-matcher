from pathlib import Path

import pytest

from parser import ParsedResume, parse_text

FIXTURE = Path(__file__).parent / "fixtures" / "sample_resume.txt"


def get_text() -> str:
    return FIXTURE.read_text()


def test_parse_name():
    result = parse_text(get_text())
    assert result.name == "John Doe"


def test_parse_email():
    result = parse_text(get_text())
    assert result.email == "john.doe@example.com"


def test_parse_skills():
    result = parse_text(get_text())
    skill_lower = [s.lower() for s in result.skills]
    assert "python" in skill_lower
    assert "fastapi" in skill_lower
    assert "docker" in skill_lower


def test_parse_experience_years():
    result = parse_text(get_text())
    # 2020-2023 = 3yrs, 2018-2020 = 2yrs → 5
    assert result.total_years_experience == 5.0


def test_parse_location():
    result = parse_text(get_text())
    assert result.city == "New York"
    assert result.country == "USA"


def test_parse_education():
    result = parse_text(get_text())
    assert "Computer Science" in result.education


def test_returns_parsed_resume_type():
    result = parse_text(get_text())
    assert isinstance(result, ParsedResume)
