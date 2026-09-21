# InsightAI

Ask business questions in natural language and get answers computed from a real PostgreSQL warehouse. The model never invents numbers: Groq picks tools or a validated read-only SELECT, FastAPI runs them, and the canvas (KPIs + charts) follows the same filters as the chat.

**Live demo:** https://insightai-frontend.vercel.app  
**Stack:** FastAPI · PostgreSQL (Nortec retail, mar 2024–sep 2026) · Groq tool calling · Next.js 15

InsightAI is a conversational BI workspace. A user asks a question in Spanish, the backend computes real metrics from PostgreSQL, and Groq turns those verified facts into a clear answer. The LLM **does not execute SQL on its own**.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Groq](https://img.shields.io/badge/Groq-1.6-orange)

## Quick start

InsightAI es un monorepo: **backend** (FastAPI) y **frontend** (Next.js) son carpetas separadas. No hay `npm run dev` en la raíz del repo salvo los scripts de conveniencia abajo.

1. **Start PostgreSQL** (Docker Desktop must be running):
   ```powershell
   docker compose up -d
   ```
   > compose fails fast if `POSTGRES_PASSWORD` is not set — see `.env.example` at the repo root, and copy it to `.env`.

2. **Cargar el warehouse Nortec** (~190k líneas de ventas, estrella dim/fact, mar 2024–sep 2026). Con Docker arriba y `backend/.env` apuntando a `localhost:5433`:
   ```powershell
   cd backend
   .\.venv\Scripts\Activate.ps1
   python -m scripts.seed_nortec
   ```
   Demo rápida (menos filas): `python -m scripts.seed_nortec --rows 8000`. El script es determinista (`--seed 42`) y recrea el schema (`schema_nortec.sql`).

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

5. **Run the API** (desde `backend/`, con el venv activado):
   ```powershell
   cd backend
   .\.venv\Scripts\Activate.ps1
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   Open http://127.0.0.1:8000 — Swagger: http://127.0.0.1:8000/docs.

   **Atajo desde la raíz del repo** (PowerShell/cmd, con venv ya creado en `backend/.venv`):
   ```powershell
   npm run dev:backend
   ```

6. **Use it**:
   ```powershell
   Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/chat" `
     -Method Post -ContentType "application/json; charset=utf-8" `
     -Body '{"question":"Cuál es el total de ventas?"}' `
     | ConvertTo-Json
   ```

### Frontend (Next.js + three.js)

> Requires Node 22+. The backend must listen on **http://127.0.0.1:8000**.

```powershell
cd frontend
npm install
npm run dev          # open http://127.0.0.1:3000
```

Desde la raíz del repo: `npm run dev:frontend` (en otra terminal, con el backend ya en marcha).

`next.config.ts` rewrites `/api/*` to `http://127.0.0.1:8000/api/*` during local development. Start the FastAPI server before using metrics or chat.

## How it works

```
User question
      │
      ▼
┌─────────────┐     tool calling loop (Groq)
│  FastAPI    │──▶  SQL tools: KPIs, series, rankings, mix…
│  /api/v1/   │     consultar_sql → validator → read-only SELECT
│  chat       │◀──  answer + tools[] + ViewSpec → canvas React
└─────────────┘
      │
      ▼
  PostgreSQL Nortec (~190k fact_ventas, mar 2024–sep 2026)
```

- **Tool calling**: the model must use tools for numbers; the API returns `{ answer, tools[], view? }` for auditability and UI sync.
- **Validated SQL**: ad-hoc questions use `consultar_sql` with allowlisted `SELECT` only (optional read-only DB user locally).
- **Safe errors**: 503/401/429/500 with sanitized messages; raw exceptions stay in server logs only.

## API

| Method | Path          | Description                                 |
|--------|---------------|---------------------------------------------|
| GET    | `/`           | Service banner                              |
| GET    | `/health`     | Liveness + PostgreSQL ping (`fact_ventas_rows`) |
| GET    | `/api/v1/metrics` | `{ view: { period, kpis, charts } }` workspace default |
| POST   | `/api/v1/chat`| `{ question, history? }` → `{ answer, tools, view? }` |

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
| `test_tools.py`         | unit        | Tool registry + executors             |
| `test_sql_validator.py` | unit        | Read-only SELECT guard                |
| `test_groq_client.py`   | unit        | Groq tool loop (mocked)               |
| `test_chat_endpoint.py` | unit        | `/chat` contract (mocked)             |
| `test_chat_schema.py`   | unit        | Input validation                    |
| `test_metrics_endpoint.py` | integration | `/metrics` — skips if DB is down |
| `test_ventas_db.py`     | integration | Real PostgreSQL fetch — **skips** honestly when no DB is available |

## Project structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app — orchestration only
│   ├── config.py                # Env-based settings (pydantic-settings)
│   ├── schemas/chat.py          # Request/response validation
│   └── services/
│       ├── data_analysis.py     # Pure Python metrics
│       ├── tools.py             # Tool calling registry + executors
│       ├── sql_validator.py     # Read-only SELECT validation
│       ├── groq_client.py       # Groq tool-calling loop
│       └── ventas_db.py         # PostgreSQL access + validated SELECT
├── tests/                       # Unit + integration tests
├── requirements.txt             # Pinned dependencies
└── setup_db.sql                 # Schema + seed data
docker-compose.yml               # PostgreSQL 15 service
frontend/                        # Next.js 15 UI (metrics 3D + chat)
```

## Public demo

Deploy the API (Render blueprint in `render.yaml`) and the Next.js app on Vercel (`frontend/`, set `NEXT_PUBLIC_API_URL`). Step-by-step: [DEPLOY.md](./DEPLOY.md).

The UI uses **demo sales data** seeded in PostgreSQL — not a real client dataset.

## Roadmap

- [x] FastAPI API + Groq chat
- [x] PostgreSQL + Python data analysis
- [x] Tests (unit + real DB integration)
- [x] Read-only SQL via `consultar_sql` (validated SELECT)
- [x] Next.js frontend to chat with the API and visualize metrics

## Requirements

- Windows / macOS / Linux, PowerShell or bash
- Python 3.12+
- Docker Desktop (for PostgreSQL)
- A Groq API key (free tier available)