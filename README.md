# InsightAI

Ask business questions in natural language and get data-driven answers computed from a real database, with an AI layer that never invents numbers.

InsightAI is an AI-powered data analysis API. A user asks a question in Spanish, the backend computes real metrics from PostgreSQL using Python, and an LLM (Groq) turns those verified facts into a clear, conversational answer.

The LLM **never generates or executes SQL** and **never generalizes beyond the computed facts**: Python owns the data, the model summarizes it. This keeps the system safe, verifiable, and honest — no hallucinated numbers.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Groq](https://img.shields.io/badge/Groq-1.6-orange)

## Quick start

1. **Start PostgreSQL** (Docker Desktop must be running):
   ```powershell
   docker compose up -d
   ```
   > compose fails fast if `POSTGRES_PASSWORD` is not set — see `.env.example` at the repo root, and copy it to `.env`.

2. **Create the database and seed data** (byte-safe: copy the script into the container and run psql inside it, so UTF-8 accents are never mangled by the shell):
   ```powershell
   docker cp backend/setup_db.sql insight_ai_postgres:/tmp/setup_db.sql
   docker exec insight_ai_postgres psql -U insight_ai -d insight_ai -f /tmp/setup_db.sql
   ```
   The script is idempotent — running it again inserts nothing. To rebuild from scratch, drop the table first:
   ```powershell
   docker exec insight_ai_postgres psql -U insight_ai -d insight_ai -c "DROP TABLE IF EXISTS ventas;"
   ```

3. **Configure the backend**: copy `backend/.env.example` to `backend/.env` and set your keys:
   ```powershell
   Copy-Item backend/.env.example backend/.env
   ```
   Required: `GROQ_API_KEY`, `GROQ_MODEL`. PostgreSQL defaults point at the Docker container (`localhost:5433`).

4. **Install dependencies** (project virtual environment):
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

5. **Run the API**:
   ```powershell
   python -m uvicorn app.main:app --reload
   ```
   Open http://localhost:8000 — the interactive Swagger docs are at http://localhost:8000/docs.

6. **Use it**:
   ```powershell
   Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/chat" `
     -Method Post -ContentType "application/json; charset=utf-8" `
     -Body '{"question":"Cuál es el total de ventas?"}' `
     | ConvertTo-Json
   ```

### Frontend (Angular + three.js)

> Scaffold created with Angular CLI 18. Requires Node 22+.

```powershell
cd frontend
npm install
npm start           # open http://127.0.0.1:4200
```

The dev server proxies `/api/*` requests to `http://127.0.0.1:8000` (see `proxy.conf.json`) — the backend must be running for data to appear.

## How it works

```
User question
      │
      ▼
┌─────────────┐   ┌──────────────────┐   ┌──────────────────────┐
│  FastAPI    │──▶│  Python metrics   │──▶│  Groq LLM (no SQL)   │
│  /api/v1/   │   │  total, promedio, │   │  summarizes facts    │
│  chat       │◀──│  max, min, by     │◀──│  only — never invents│
│             │   │  category         │   │  numbers             │
└─────────────┘   └──────────────────┘   └──────────────────────┘
      │
      ▼
  PostgreSQL (Docker, port 5433)
  ventas table — fixed read-only SQL
```

- **Fixed SQL only**: `ventas_db.py` runs a static `SELECT`. The LLM has no database access and no SQL-generation rights.
- **Facts first**: all metrics are computed in Python and passed to the model as ground truth.
- **Safe errors**: 503/401/429/500 with sanitized messages; raw exceptions stay in server logs only.

## API

| Method | Path          | Description                                 |
|--------|---------------|---------------------------------------------|
| GET    | `/`           | Service banner                              |
| GET    | `/health`     | Liveness check                              |
| GET    | `/api/v1/metrics` | Structured metrics (for charts / 3D viz) |
| POST   | `/api/v1/chat`| `{ "question": "..." }` → `{ "answer": "..." }` |

## Environment variables

| Variable          | Required | Default     | Description                    |
|-------------------|----------|-------------|--------------------------------|
| `GROQ_API_KEY`    | yes      | —           | Groq API key                   |
| `GROQ_MODEL`      | yes      | —           | Groq model id                  |
| `POSTGRES_HOST`   | no       | `localhost` | Postgres host                  |
| `POSTGRES_PORT`   | no       | `5433`      | Postgres port (Docker mapping) |
| `POSTGRES_DB`     | no       | `insight_ai`| Database name                  |
| `POSTGRES_USER`   | no       | `insight_ai`| Database user                  |
| `POSTGRES_PASSWORD`| no*     | empty       | Database password              |
| `POSTGRES_PASSWORD` (compose, root `.env`) | yes | — | Used by `docker compose` — fails fast if missing |

\* `POSTGRES_PASSWORD` defaults to empty in the backend; Docker Compose **requires** it in a root `.env`.

## Tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests -v
```

| Suite                 | Type         | Covers                              |
|-----------------------|--------------|-------------------------------------|
| `test_data_analysis.py` | unit        | All metrics + empty-data edge cases  |
| `test_chat_schema.py`   | unit        | Input validation                    |
| `test_ventas_db.py`     | integration | Real PostgreSQL fetch — **skips** honestly when no DB is available, never fakes success |

## Project structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app — orchestration only
│   ├── config.py                # Env-based settings (pydantic-settings)
│   ├── schemas/chat.py          # Request/response validation
│   └── services/
│       ├── data_analysis.py     # Pure Python metrics
│       ├── groq_client.py       # Groq boundary — typed error mapping
│       └── ventas_db.py         # PostgreSQL data access (fixed SQL)
├── tests/                       # Unit + integration tests
├── requirements.txt             # Pinned dependencies
└── setup_db.sql                 # Schema + seed data
docker-compose.yml               # PostgreSQL 15 service
```

## Roadmap

- [x] FastAPI API + Groq chat
- [x] PostgreSQL + Python data analysis
- [x] Tests (unit + real DB integration)
- [ ] Read-only SQL generation from questions (safe, validated) — or a frontend (Angular) to chat with the API

## Requirements

- Windows / macOS / Linux, PowerShell or bash
- Python 3.12+
- Docker Desktop (for PostgreSQL)
- A Groq API key (free tier available)