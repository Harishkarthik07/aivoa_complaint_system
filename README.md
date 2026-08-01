# AIVOA – AI-Powered Customer Complaint Management System

A Customer Complaint Management module for a pharmaceutical manufacturing QMS, built for the
AIVOA Round 1 Full Stack Developer Assessment.

## Stack

- **Frontend:** React + Redux Toolkit, React Router, Google Inter font
- **Backend:** FastAPI + SQLAlchemy
- **AI Agents:** LangGraph pipeline calling Groq (`llama-3.3-70b-versatile`, fallback `llama-3.3-70b-versatile`)
- **Database:** PostgreSQL 

## Architecture

```
frontend/  React + Redux SPA — complaint intake form, dashboard, detail view
backend/
  app/
    core/       config + DB session
    models/     SQLAlchemy models (Complaint)
    schemas/    Pydantic request/response schemas
    agents/     LangGraph pipeline + individual AI nodes + Groq client
    routers/    FastAPI route handlers
    main.py     app entrypoint
  seed_data.py  populates sample pharma complaints (runs them through the AI pipeline too)
```

### AI Pipeline (LangGraph)

On every new complaint, a 5-node graph runs sequentially:

```
completeness_check -> risk_classification -> summary -> root_cause_capa -> duplicate_detection
```

1. **Completeness Checker** — scores whether the complaint has enough info to investigate, flags missing fields
2. **Risk Classification** — Low / Medium / High / Critical, per pharma QMS safety-risk conventions
3. **Complaint Summary** — 2-3 sentence investigator-facing summary
4. **Root Cause + CAPA Recommendation** — preliminary hypothesis and corrective/preventive action suggestion
5. **Duplicate Detection** — compares against recent complaints for the same product to flag likely duplicates

Each node is independent (reads/writes its own state keys), so nodes can be reordered or
parallelized later without rewriting pipeline logic.

## Setup

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
# edit .env: set DATABASE_URL and GROQ_API_KEY (get one at https://console.groq.com)
uvicorn app.main:app --reload --port 8000
```

Optional: seed sample complaints (also exercises the AI pipeline):

```bash
python seed_data.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. The Vite dev server proxies `/api` requests to
`http://localhost:8000` (see `vite.config.js`).

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/complaints` | Create a complaint (multipart form, optional attachment); runs full AI pipeline before saving |
| GET | `/api/complaints` | List complaints, filterable by `status` and `severity` |
| GET | `/api/complaints/{id}` | Get one complaint with all AI analysis fields |
| PATCH | `/api/complaints/{id}/status` | Update complaint status (New → Under Investigation → CAPA Initiated → Closed) |
| GET | `/api/health` | Health check |

## Notes on scope / assumptions

- This scaffold assumes a workflow of: intake → automatic AI analysis → dashboard triage →
  manual status progression through investigation and CAPA. If the reference demo video shows
  a different flow (e.g. a review/approval step before AI analysis, or additional QMS stages),
  the `complaints.py` router and `ComplaintStatus` enum are the places to adjust.
- OCR/document parsing of uploaded PDFs/emails is out of scope per the assignment (attachments
  are stored but not parsed) — this would be a natural next LangGraph node to add.
- All AI outputs (summary, root cause, CAPA, risk) are hypotheses for a human investigator, not
  final QA decisions — this is reflected in the prompts.

