import asyncio
import json
from dataclasses import dataclass

from openai import AsyncOpenAI

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI()
    return _client


SYSTEM_PROMPT = """You are an expert HR analyst. Given a Job Description and a Resume, \
score the match across four dimensions and provide brief reasoning for each.

Respond ONLY with valid JSON — no markdown fences, no extra text — matching this exact schema:
{
  "total_score": <integer 0-100>,
  "skills_score": <integer 0-100>,
  "experience_score": <integer 0-100>,
  "location_score": <integer 0-100>,
  "education_score": <integer 0-100>,
  "skills_reasoning": "<one sentence>",
  "experience_reasoning": "<one sentence>",
  "location_reasoning": "<one sentence>",
  "education_reasoning": "<one sentence>",
  "recommendation": "<2-3 sentence hire recommendation>"
}

Scoring guidance:
- skills_score: overlap between required and candidate skills (keywords + depth)
- experience_score: required years vs candidate's years and seniority
- location_score: proximity match; remote role or remote candidate = 100
- education_score: required degree level vs candidate's degree
- total_score: weighted average (skills 40%, experience 30%, location 20%, education 10%)"""


@dataclass
class AIScoreResult:
    total_score: float
    skills_score: float
    experience_score: float
    location_score: float
    education_score: float
    skills_reasoning: str
    experience_reasoning: str
    location_reasoning: str
    education_reasoning: str
    recommendation: str


async def score_ai(jd_text: str, resume_text: str) -> AIScoreResult:
    data = await _call_openai(jd_text, resume_text)
    return AIScoreResult(**data)


async def score_all_ai(
    jd_text: str, resume_texts: list[str]
) -> list[AIScoreResult | Exception]:
    tasks = [score_ai(jd_text, text) for text in resume_texts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return list(results)


async def _call_openai(jd_text: str, resume_text: str) -> dict:
    response = await _get_client().chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"JOB DESCRIPTION:\n{jd_text}\n\n"
                    f"---\n\nRESUME:\n{resume_text}"
                ),
            },
        ],
        temperature=0.2,
    )
    return json.loads(response.choices[0].message.content)
