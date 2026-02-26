import io

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

JD_TXT = (
    b"Software Engineer - Python\n"
    b"New York, NY, USA\n"
    b"We need 2 years of experience.\n"
    b"Skills: Python, Docker, SQL\n"
    b"Education: B.Sc Computer Science\n"
)

RESUME_TXT = (
    b"Jane Smith\n"
    b"jane@example.com\n"
    b"New York, NY, USA\n"
    b"Skills: Python, Docker, SQL, React\n"
    b"Software Engineer at Tech Corp (2021 - 2024)\n"
    b"B.Sc Computer Science, NYU, 2021\n"
)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_score_algorithmic_returns_results():
    files = [
        ("jd",      ("jd.txt",     io.BytesIO(JD_TXT),     "text/plain")),
        ("resumes", ("resume1.txt", io.BytesIO(RESUME_TXT), "text/plain")),
    ]
    r = client.post("/api/score?mode=algorithmic", files=files)
    assert r.status_code == 200
    data = r.json()
    assert data["mode"] == "algorithmic"
    assert len(data["results"]) == 1
    item = data["results"][0]
    assert "total_score" in item
    assert "skills_score" in item
    assert "experience_score" in item
    assert "location_score" in item
    assert "education_score" in item
    assert 0 <= item["total_score"] <= 100


def test_score_multiple_resumes():
    files = [
        ("jd",      ("jd.txt", io.BytesIO(JD_TXT), "text/plain")),
        ("resumes", ("r1.txt", io.BytesIO(RESUME_TXT), "text/plain")),
        ("resumes", ("r2.txt", io.BytesIO(b"Bob Jones\nbob@example.com\nPython developer"), "text/plain")),
    ]
    r = client.post("/api/score?mode=algorithmic", files=files)
    assert r.status_code == 200
    assert len(r.json()["results"]) == 2


def test_unsupported_file_format_rejected():
    files = [
        ("jd",      ("jd.exe",     io.BytesIO(b"data"), "application/octet-stream")),
        ("resumes", ("resume.txt", io.BytesIO(RESUME_TXT), "text/plain")),
    ]
    r = client.post("/api/score?mode=algorithmic", files=files)
    assert r.status_code == 400


def test_too_many_resumes_rejected():
    resume_file = ("resumes", ("r.txt", io.BytesIO(b"Candidate"), "text/plain"))
    files = [("jd", ("jd.txt", io.BytesIO(JD_TXT), "text/plain"))] + [resume_file] * 11
    r = client.post("/api/score?mode=algorithmic", files=files)
    assert r.status_code == 400


def test_results_sorted_descending():
    high = (
        b"Alice Top\nalice@ex.com\nNew York, NY, USA\n"
        b"Skills: Python, Docker, SQL, React, TypeScript, FastAPI\n"
        b"Senior Engineer (2018 - 2024)\nB.Sc Computer Science\n"
    )
    low = b"Bob Low\nbob@ex.com\nTokyo, Japan\nSkills: Java\n1 year experience\n"
    files = [
        ("jd",      ("jd.txt",   io.BytesIO(JD_TXT), "text/plain")),
        ("resumes", ("high.txt", io.BytesIO(high),    "text/plain")),
        ("resumes", ("low.txt",  io.BytesIO(low),     "text/plain")),
    ]
    r = client.post("/api/score?mode=algorithmic", files=files)
    results = r.json()["results"]
    scores = [res["total_score"] for res in results]
    assert scores == sorted(scores, reverse=True)
