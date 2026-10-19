"""End-to-end smoke test: the real app, a throwaway SQLite database and the mock providers.

Imports app.main, so a module imported by any router but missing from pyproject.toml fails here
(the unit tests never import the app). Then one lead goes through create → enrich → score.
"""

import os
import tempfile
import uuid

# A fresh database file per run (CI may set DATABASE_URL itself; then that one is used).
_DB = os.path.join(tempfile.mkdtemp(prefix="qualisift-smoke-"), "smoke.db")
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{_DB}")
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("ENRICHMENT_PROVIDER", "mock")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(scope="module")
def client():
    from app.db.seed import seed_criteria
    from app.db.session import async_session_factory, init_db
    from app.main import app

    with TestClient(app) as c:
        # Scoring needs the five criteria; seed them the same way the seed script does.
        async def prepare() -> None:
            await init_db()
            async with async_session_factory() as session:
                await seed_criteria(session)
                await session.commit()

        c.portal.call(prepare)
        yield c


def test_health(client: TestClient) -> None:
    assert client.get("/api/v1/health").status_code == 200


def test_lead_is_enriched_and_scored(client: TestClient) -> None:
    created = client.post(
        "/api/v1/leads",
        json={
            "email": f"smoke-{uuid.uuid4().hex[:8]}@acme.example",
            "first_name": "Sam",
            "company": "Acme",
            "company_domain": "acme.example",
            "job_title": "Head of Operations",
        },
    )
    assert created.status_code == 202, created.text  # accepted; scoring runs in the background
    lead_id = created.json()["data"]["lead_id"]
    # TestClient runs background tasks before returning, so scoring has finished here.
    lead = client.get(f"/api/v1/leads/{lead_id}").json()["data"]
    assert lead["status"] == "scored"
    composite = lead["composite_score"]["composite_score"]
    assert 0 <= composite <= 100
    assert len(lead["scores"]) == 5
