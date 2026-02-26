import os
import tempfile
from typing import List

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from extractor import extract_text, ALLOWED_EXTENSIONS
from parser import parse_text
from scorer_algo import score_algorithmic
from scorer_ai import score_all_ai

app = FastAPI(title="JD Matcher API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/score")
async def score_resumes(
    jd: UploadFile = File(..., description="Job description file (PDF/DOCX/TXT)"),
    resumes: List[UploadFile] = File(..., description="Up to 10 resume files"),
    mode: str = Query("algorithmic", enum=["algorithmic", "ai"]),
):
    if len(resumes) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 resumes allowed.")

    # Parse JD
    jd_text = await _read_upload(jd)
    jd_parsed = parse_text(jd_text)

    # Parse resumes
    resume_texts: list[str] = []
    filenames: list[str] = []
    for r in resumes:
        text = await _read_upload(r)
        resume_texts.append(text)
        filenames.append(r.filename or f"resume_{len(filenames)+1}")

    if mode == "algorithmic":
        results = []
        for filename, text in zip(filenames, resume_texts):
            parsed = parse_text(text)
            score  = score_algorithmic(jd_parsed, parsed)
            results.append(
                {
                    "filename": filename,
                    "candidate_name": parsed.name or filename,
                    "total_score": score.total_score,
                    "skills_score": score.skills_score,
                    "experience_score": score.experience_score,
                    "location_score": score.location_score,
                    "education_score": score.education_score,
                    "mode": "algorithmic",
                }
            )

    else:  # ai
        ai_outcomes = await score_all_ai(jd_text, resume_texts)
        results = []
        for filename, outcome in zip(filenames, ai_outcomes):
            if isinstance(outcome, Exception):
                results.append(
                    {
                        "filename": filename,
                        "candidate_name": filename,
                        "total_score": 0,
                        "skills_score": 0,
                        "experience_score": 0,
                        "location_score": 0,
                        "education_score": 0,
                        "error": str(outcome),
                        "mode": "ai",
                    }
                )
            else:
                results.append(
                    {
                        "filename": filename,
                        "candidate_name": filename,
                        "total_score": outcome.total_score,
                        "skills_score": outcome.skills_score,
                        "experience_score": outcome.experience_score,
                        "location_score": outcome.location_score,
                        "education_score": outcome.education_score,
                        "skills_reasoning": outcome.skills_reasoning,
                        "experience_reasoning": outcome.experience_reasoning,
                        "location_reasoning": outcome.location_reasoning,
                        "education_reasoning": outcome.education_reasoning,
                        "recommendation": outcome.recommendation,
                        "mode": "ai",
                    }
                )

    results.sort(key=lambda x: x.get("total_score", 0), reverse=True)
    return {"results": results, "mode": mode}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _read_upload(upload: UploadFile) -> str:
    filename = upload.filename or ""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}' for '{filename}'. Allowed: PDF, DOCX, TXT.",
        )
    content = await upload.read()
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        return extract_text(tmp_path)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse '{filename}': {exc}") from exc
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
