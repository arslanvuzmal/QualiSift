# Setup Guide

## Prerequisites
- **Docker path:** Docker Desktop (Compose v2).
- **Native path:** Python 3.12+ and Node.js 20+. No database required (uses SQLite).

## Docker (recommended)
```bash
cp .env.example .env
docker compose up --build
```
- Dashboard: http://localhost:3001
- API + Swagger: http://localhost:8000/docs

The `api` service runs `alembic upgrade head` → `python -m scripts.seed` → `uvicorn` on `0.0.0.0:8000`.

## Native (no Docker)
```bash
# --- API ---
cd apps/api
python -m venv .venv
. .venv/Scripts/activate        # Windows
# . .venv/bin/activate          # macOS/Linux
pip install -e ".[dev]"
printf "DATABASE_URL=sqlite+aiosqlite:///./dev.db\nLLM_PROVIDER=mock\nENRICHMENT_PROVIDER=mock\n" > .env
python -m scripts.seed
uvicorn app.main:app --host 0.0.0.0 --port 8000

# --- Web (new terminal) ---
cd apps/web
npm install
npm run dev
```

## Using real providers
Set these in `.env` (root for Docker, or `apps/api/.env` for native):
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
ENRICHMENT_PROVIDER=clearbit
CLEARBIT_API_KEY=...
```

## Verifying it works
```bash
curl http://localhost:8000/health                          # {"status":"ok"}
curl http://localhost:8000/api/v1/leads?page_size=3        # seeded leads with scores
curl -X POST http://localhost:8000/api/v1/digest/generate  # Hot/Warm/Cold counts
```

## Troubleshooting — "the link isn't working"
- **`localhost:8000` refused:** ensure the API binds to `0.0.0.0` (not `127.0.0.1`) — the compose
  command already does. Check `docker compose logs api`.
- **`localhost:3001` refused:** check `docker compose logs web` shows Next.js "Ready".
- **Frontend loads but no data:** confirm `NEXT_PUBLIC_API_URL=http://localhost:8000` (browser-facing,
  not the internal `api` service name) and that CORS allows `http://localhost:3001` (it does by default).
- **DB errors on API start (Docker):** Postgres must be healthy first — `depends_on: condition:
  service_healthy` handles ordering; re-run `docker compose up` if the first boot raced.
- **Port already in use:** stop whatever holds 8000/3001/5432/6379, or change the host port mappings.

## Running tests
```bash
cd apps/api && pytest        # 86 tests
cd apps/web && npm run type-check
```
