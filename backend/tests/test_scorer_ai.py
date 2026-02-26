import pytest
from unittest.mock import AsyncMock, patch

from scorer_ai import AIScoreResult, score_ai

MOCK_RESPONSE = {
    "total_score": 82,
    "skills_score": 90,
    "experience_score": 80,
    "location_score": 70,
    "education_score": 85,
    "skills_reasoning": "Strong Python and FastAPI match.",
    "experience_reasoning": "Candidate has 5 years vs 3 required.",
    "location_reasoning": "Both in same country.",
    "education_reasoning": "Degree level matches requirement.",
    "recommendation": "Strong candidate with relevant skills. Recommend for interview.",
}


@pytest.mark.asyncio
async def test_score_ai_returns_structured():
    with patch("scorer_ai._call_openai", new=AsyncMock(return_value=MOCK_RESPONSE)):
        result = await score_ai("JD text here", "Resume text here")

    assert isinstance(result, AIScoreResult)
    assert result.total_score == 82
    assert result.skills_score == 90
    assert result.experience_score == 80
    assert result.location_score == 70
    assert result.education_score == 85
    assert "Strong Python" in result.skills_reasoning
    assert "interview" in result.recommendation


@pytest.mark.asyncio
async def test_score_ai_all_fields_present():
    with patch("scorer_ai._call_openai", new=AsyncMock(return_value=MOCK_RESPONSE)):
        result = await score_ai("JD", "Resume")

    assert result.skills_reasoning
    assert result.experience_reasoning
    assert result.location_reasoning
    assert result.education_reasoning
    assert result.recommendation
