# JD Matcher 🎯

A single-page application that matches a Job Description against up to 10 resumes and ranks candidates by relevance. Supports two independent scoring approaches — **Algorithmic** (no API cost, fully explainable) and **AI-powered** (GPT-4o, deeper semantic understanding).

---

## Demo

![JD Matcher UI](https://placehold.co/900x500?text=Upload+JD+%2B+Resumes+%E2%80%94+Get+Ranked+Results)

---

## Features

- Upload **1 JD** + up to **10 resumes** (PDF, DOCX, TXT)
- Two scoring approaches selectable from the dashboard
- Per-dimension score breakdown: Skills · Experience · Location · Education
- Colour-coded badges (🟢 ≥70 · 🟡 40–69 · 🔴 <40)
- Top-3 candidate side-by-side comparison panel
- Expandable rows with AI reasoning text (AI mode)
- CSV export of all results
- Fully Dockerised — one command deploy

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 · TypeScript · Vite · Tailwind CSS v4 |
| Backend | Python 3.12 · FastAPI · Uvicorn |
| Parsing | pdfplumber · python-docx · spaCy (en_core_web_sm) |
| Algorithmic scoring | scikit-learn (TF-IDF · cosine similarity) |
| AI scoring | OpenAI GPT-4o (structured JSON output) |
| Containerisation | Docker · Docker Compose |

---

## Scoring Approaches

### Approach 1 — Algorithmic (No AI)

A transparent, deterministic scoring pipeline built on classical NLP techniques. Runs entirely on your machine with **no API calls and no cost**.

#### How it works

Each resume is independently scored against the JD across four weighted dimensions, then combined into a final score (0–100).

| Dimension | Weight | Method |
|---|---|---|
| **Skills Match** | 40% | Keyword overlap (60%) + TF-IDF cosine similarity (40%) |
| **Experience Match** | 30% | Required years vs extracted years from date ranges / explicit mentions |
| **Location Match** | 20% | Proximity scoring — city / state / country hierarchy |
| **Education Match** | 10% | Degree-level keyword matching |

#### Skills scoring in detail

1. **Keyword overlap** — a curated list of 50+ technology skills is checked against both the JD and resume using regex boundary matching. The fraction of JD-required skills found in the resume is the keyword score.
2. **TF-IDF cosine similarity** — both documents are vectorised using Term Frequency–Inverse Document Frequency. The cosine angle between the vectors captures broader vocabulary similarity beyond exact keyword matches.
3. Final skills score = `keyword_score × 0.6 + tfidf_score × 0.4`, capped at 100.

#### Experience scoring in detail

The parser extracts total experience by:
- Finding date ranges in the resume text (e.g. `2020 – 2024`, `2019 – Present`) and summing durations
- Falling back to explicit mentions (e.g. "5 years of experience")

Candidate years are compared to the JD's required years:
- Candidate ≥ required → 100%
- Candidate < required → `(candidate / required) × 100`

#### Location scoring in detail

Proximity is scored on a three-tier hierarchy:

| Match level | Score |
|---|---|
| Same city | 100% |
| Same state / province | 60% |
| Same country | 30% |
| No match | 0% |
| Remote in JD **or** resume | 100% (overrides all) |

#### Education scoring in detail

The parser identifies the highest degree mentioned in the JD and the resume, classifying them into three tiers (Bachelor → Master → PhD). A match at the required tier returns 100%; a lower tier returns 30%; no education requirement in the JD returns 100% for everyone.

#### Final score formula

```
total = skills × 0.40 + experience × 0.30 + location × 0.20 + education × 0.10
```

**Best for:** quick screening, offline environments, auditable results, no API budget.

---

### Approach 2 — AI-Powered (GPT-4o)

Uses OpenAI's GPT-4o model with **structured JSON output** to perform a holistic semantic match. The model reads the full JD and resume text and reasons about fit the way a human recruiter would.

#### How it works

1. **Concurrent processing** — all resumes are sent to the OpenAI API simultaneously using Python `asyncio.gather`, keeping total latency close to a single call.
2. **Structured prompt** — a system prompt instructs GPT-4o to act as an expert HR analyst and return a fixed JSON schema with no free-form text outside the schema.
3. **JSON mode** — `response_format: { type: "json_object" }` is enforced so the response is always valid, machine-parseable JSON.

#### What GPT-4o evaluates

| Field | Description |
|---|---|
| `skills_score` | Semantic skill overlap — understands synonyms, adjacent technologies, and implied skills from job titles |
| `experience_score` | Evaluates depth, relevance, and seniority of experience, not just total years |
| `location_score` | Understands remote/hybrid signals, relocation willingness phrasing |
| `education_score` | Considers field of study relevance, not just degree level |
| `total_score` | GPT-4o's own weighted overall match (roughly: skills 40%, exp 30%, loc 20%, edu 10%) |
| `*_reasoning` | One-sentence explanation per dimension |
| `recommendation` | 2–3 sentence hire recommendation |

#### Example AI response

```json
{
  "total_score": 84,
  "skills_score": 91,
  "experience_score": 80,
  "location_score": 70,
  "education_score": 95,
  "skills_reasoning": "Candidate has strong Python, FastAPI and Docker experience directly matching the JD requirements.",
  "experience_reasoning": "5 years of relevant engineering experience exceeds the 3-year requirement.",
  "location_reasoning": "Candidate is based in a different country with no remote preference stated.",
  "education_reasoning": "B.Sc. in Computer Science directly aligns with the role requirements.",
  "recommendation": "Strong technical match with demonstrated experience in all key areas. The location mismatch is the only concern — recommend a remote interview to assess flexibility."
}
```

#### Error handling

- If an individual OpenAI call fails (rate limit, network error), that resume is flagged with an error message in the UI. Other results are still shown.
- A fallback prompt in the UI suggests switching to Algorithmic mode if the API key is missing.

**Best for:** deep semantic matching, nuanced role requirements, senior/specialist hiring, when explainability per candidate is needed.

---

## Approach Comparison

| | Algorithmic | AI (GPT-4o) |
|---|---|---|
| **API cost** | Free | ~$0.01–0.05 per 10 resumes |
| **Speed** | < 1 second | 5–15 seconds |
| **Explainability** | Full formula breakdown | Natural language reasoning |
| **Semantic understanding** | Keyword-level | Human-level |
| **Works offline** | ✅ | ❌ (requires internet) |
| **Consistent results** | ✅ Always identical | ✅ (temperature=0.2) |
| **Handles synonyms** | Partial (TF-IDF) | ✅ Full |

---

## Quick Start

### With Docker (recommended)

```bash
git clone https://github.com/Hemanth-stack/JD-matcher.git
cd JD-matcher
cp .env.example .env          # Add your OPENAI_API_KEY for AI mode
make deploy
```

Open **http://localhost:5173**

### Without Docker (local dev)

```bash
# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --app-dir backend --host 0.0.0.0 --port 8080 --reload

# Frontend (new terminal)
npm --prefix frontend install
npm --prefix frontend run dev -- --host
```

---

## Makefile Commands

```bash
make deploy         # Build Docker images and start all services (one command)
make dev            # Run backend + frontend locally without Docker
make test           # Run all 33 backend tests (pytest)
make down           # Stop Docker containers
make logs           # Tail Docker logs
make build          # Build frontend for production
make clean          # Remove containers, venv, node_modules
make help           # List all available commands
```

---

## Project Structure

```
JD_matcher/
├── backend/
│   ├── main.py           # FastAPI app — /api/health, /api/score
│   ├── parser.py         # Extracts name, skills, experience, location, education
│   ├── extractor.py      # PDF / DOCX / TXT → plain text
│   ├── scorer_algo.py    # Algorithmic scoring (TF-IDF + weighted dimensions)
│   ├── scorer_ai.py      # GPT-4o scoring (async, structured JSON)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/            # 33 pytest tests
│       ├── test_parser.py
│       ├── test_extractor.py
│       ├── test_scorer_algo.py
│       ├── test_scorer_ai.py
│       └── test_api.py
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   ├── types.ts
│   │   ├── components/
│   │   │   ├── UploadPanel.tsx      # File upload + mode toggle
│   │   │   ├── ResultsTable.tsx     # Ranked results with expandable detail
│   │   │   ├── ComparisonPanel.tsx  # Top-3 side-by-side view
│   │   │   └── ScoreBar.tsx         # Animated score progress bar
│   │   └── utils/exportCsv.ts
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── Makefile
└── .env.example
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | For AI mode | Your OpenAI API key (`sk-...`) |

Copy `.env.example` to `.env` and fill in your key. Algorithmic mode works without any key.

---

## API Reference

### `GET /api/health`
Returns `{"status": "ok"}` — used for health checks.

### `POST /api/score?mode=algorithmic|ai`

**Form data:**
- `jd` — the job description file (PDF / DOCX / TXT)
- `resumes` — up to 10 resume files (same formats)

**Response:**
```json
{
  "mode": "algorithmic",
  "results": [
    {
      "filename": "john_doe.pdf",
      "candidate_name": "John Doe",
      "total_score": 87.3,
      "skills_score": 91.0,
      "experience_score": 100.0,
      "location_score": 60.0,
      "education_score": 100.0,
      "mode": "algorithmic"
    }
  ]
}
```

Results are sorted by `total_score` descending.

---

## Running Tests

```bash
source .venv/bin/activate
cd backend && pytest tests/ -v
```

33 tests covering: file extraction, text parsing, algorithmic scoring (all dimensions), AI scorer (mocked), and full API endpoints.

---

## License

MIT
