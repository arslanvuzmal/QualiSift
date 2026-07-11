"""
Scoring service.

Bridges the persistence layer (SQLAlchemy models) with the LangGraph scoring
agent. Given a lead id, it loads the lead + active criteria, runs the agent,
and persists the per-criterion ``Score`` rows and the aggregated
``CompositeScore``, then advances the lead's status.

This is the function the API's background tasks call, so a single lead flows
end-to-end: ingest -> enrich -> score -> persist -> digest.
"""

from __future__ import annotations

import time
import uuid

import structlog
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import score_lead_async
from app.config import settings
from app.models.criteria import CriteriaConfig
from app.models.lead import Lead, LeadStatus
from app.models.score import CompositeScore, Score
from app.services.enrichment import get_enrichment_adapter

logger = structlog.get_logger(__name__)


def _lead_to_scoring_dict(lead: Lead) -> dict:
    """Flatten a Lead ORM row into the dict the agent/validator expects.

    Enriched fields are lifted to the top level so both the prompt builder and
    the anti-hallucination validator can see them as first-class evidence.
    """
    data: dict = {
        "email_hash": lead.email_hash,
        "first_name": lead.first_name,
        "last_name": lead.last_name,
        "company": lead.company,
        "company_domain": lead.company_domain,
        "job_title": lead.job_title,
        "source": lead.source,
        "status": lead.status.value if lead.status else None,
        "raw_payload": lead.raw_payload or {},
    }
    if lead.enriched_data:
        for key, value in lead.enriched_data.items():
            data.setdefault(key, value)
    return data


async def _ensure_enriched(session: AsyncSession, lead: Lead) -> None:
    """Populate ``lead.enriched_data`` via the configured enrichment adapter."""
    if lead.enriched_data:
        return
    adapter = get_enrichment_adapter()
    enriched = await adapter.enrich_by_email(lead.email)
    lead.enriched_data = enriched.model_dump()
    if lead.status == LeadStatus.NEW:
        lead.status = LeadStatus.ENRICHED
    await session.flush()
    logger.info("Lead enriched", lead_id=str(lead.id), provider=settings.ENRICHMENT_PROVIDER)


async def score_lead_and_persist(
    session: AsyncSession, lead_id: str | uuid.UUID
) -> dict:
    """Run the scoring agent for a lead and persist all results.

    Returns a small result dict describing the outcome. Safe to re-run: prior
    scores for the lead are replaced (idempotent re-scoring).
    """
    lead = await session.get(Lead, uuid.UUID(str(lead_id)))
    if lead is None:
        logger.warning("Cannot score - lead not found", lead_id=str(lead_id))
        return {"success": False, "error": "Lead not found"}

    await _ensure_enriched(session, lead)

    # Load active scoring criteria (highest weight first).
    result = await session.execute(
        select(CriteriaConfig)
        .where(CriteriaConfig.is_active.is_(True))
        .order_by(CriteriaConfig.weight.desc())
    )
    criteria = result.scalars().all()
    if not criteria:
        logger.error("Cannot score - no active criteria configured")
        return {"success": False, "error": "No active criteria configured"}

    criteria_configs = [
        {
            "name": c.name,
            "display_name": c.display_name,
            "weight": c.weight,
            "is_active": c.is_active,
        }
        for c in criteria
    ]

    lead_data = _lead_to_scoring_dict(lead)

    started = time.perf_counter()
    outcome = await score_lead_async(lead_data, criteria_configs)
    latency_ms = int((time.perf_counter() - started) * 1000)

    if not outcome.get("success"):
        logger.error("Scoring failed", lead_id=str(lead.id), error=outcome.get("error"))
        return outcome

    final = outcome["result"]  # LeadScoreResult
    composite = float(outcome["composite_score"] or 0.0)
    validation = outcome.get("validation") or {}
    trace_id = uuid.uuid4().hex
    model_used = (
        settings.OPENAI_MODEL if settings.LLM_PROVIDER == "openai" else "mock"
    )

    # Replace any previous per-criterion scores (idempotent re-scoring).
    await session.execute(delete(Score).where(Score.lead_id == lead.id))
    for criterion in final.criteria_scores:
        session.add(
            Score(
                lead_id=lead.id,
                criteria_name=criterion.criteria_name,
                score=criterion.score,
                reasoning=criterion.reasoning,
                cited_evidence=criterion.cited_evidence,
                confidence=criterion.confidence,
                validation_warnings={
                    "is_valid": validation.get("is_valid"),
                    "failed_checks": validation.get("failed_checks"),
                },
                model_used=model_used,
                latency_ms=latency_ms,
                trace_id=trace_id,
            )
        )

    # Upsert the composite score.
    existing = await session.execute(
        select(CompositeScore).where(CompositeScore.lead_id == lead.id)
    )
    composite_row = existing.scalars().first()
    if composite_row is None:
        composite_row = CompositeScore(lead_id=lead.id)
        session.add(composite_row)
    composite_row.composite_score = composite
    composite_row.overall_summary = final.overall_summary
    composite_row.suggested_action = final.suggested_action
    composite_row.disqualify = final.disqualify
    composite_row.disqualify_reason = final.disqualify_reason

    lead.status = LeadStatus.DISQUALIFIED if final.disqualify else LeadStatus.SCORED

    await session.commit()
    logger.info(
        "Lead scored and persisted",
        lead_id=str(lead.id),
        composite_score=composite,
        status=lead.status.value,
        validation_ok=validation.get("is_valid"),
    )
    return {
        "success": True,
        "lead_id": str(lead.id),
        "composite_score": composite,
        "disqualify": final.disqualify,
        "status": lead.status.value,
    }


async def score_lead_by_id(lead_id: str | uuid.UUID) -> dict:
    """Convenience wrapper that opens its own session.

    Used by FastAPI background tasks, which run after the request session has
    already been closed.
    """
    from app.db.session import async_session_factory

    async with async_session_factory() as session:
        return await score_lead_and_persist(session, lead_id)
