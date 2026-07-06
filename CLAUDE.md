# CLAUDE.md — context for AI coding agents

Guidance for Claude Code / AI agents working in this repository.

## What this is
Cortex is a full-stack AI sales lead qualifier: a FastAPI + LangGraph backend that enriches and
scores leads, and a Next.js dashboard. See `README.md` for the product overview and
`docs/architecture.md` for internals.

## Monorepo layout
- `apps/api` — Python 3.12 backend (FastAPI, LangGraph, SQLAlchemy async, Pydantic v2, Alembic).
- `apps/web` — Next.js 14 App Router frontend (TypeScript strict, Tailwind, SWR, Recharts).
- `scripts/` — `init.sql` (Postgres extensions) and a root seed launcher.
- `docs/` — architecture + setup guides.

## Common commands
```bash
# Backend (from apps/api)
pip install -e ".[dev]"
python -m scripts.seed                 # create schema (SQLite/Postgres) + seed data
uvicorn app.main:app --host 0.0.0.0 --port 8000
pytest                                 # 86 tests
alembic upgrade head                   # apply migrations (Postgres)

# Frontend (from apps/web)
npm install
npm run dev
npm run type-check

# Full stack
docker compose up --build
```

## Key conventions
- **Async everywhere** in the backend: DB, HTTP, and agent calls use `async`/`await`.
- **Portable models**: use `JSONType` and `PortableUUID` from `app.db.base` (JSONB/UUID on Postgres,
  JSON/CHAR on SQLite) — do **not** import Postgres-only column types directly.
- **Structured LLM output**: the agent must return the `LeadScoreResult` Pydantic schema; never parse
  free-text JSON. New scoring providers go in `app/agents/graph.py` behind the `LLM_PROVIDER` switch.
- **Pluggable providers**: enrichment/CRM/email are adapters selected by env (`*_PROVIDER`); add a new
  provider by implementing the adapter interface and extending the factory, not by branching in services.
- **PII**: hash emails / mask phones (`app/utils/pii.py`) before anything leaves for an LLM. Never log PII or keys.
- **Logging**: `structlog.get_logger()` — no `print` in app code.
- **Config**: all settings via `app/config.py` (pydantic-settings) + env; see `.env.example`.

## Where things live
- Scoring pipeline: `app/agents/graph.py` (nodes) + `app/services/scoring.py` (persistence).
- Anti-hallucination: `app/agents/validator.py`.
- Digest: `app/services/digest.py` + `app/routers/digest.py` + `app/templates/digest_email.html`.
- Frontend data layer: `apps/web/src/lib/{api,hooks,types}.ts` (the API client already unwraps the
  `StandardResponse` envelope — hooks read `.data` directly).

## Testing expectations
- Keep `pytest` green (86 tests) and `npm run type-check` clean before committing.
- The mock providers make the whole pipeline runnable with no API keys — prefer them in tests.
