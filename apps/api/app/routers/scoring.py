"""
FastAPI router for Scoring endpoints.

Handles manual triggering and re-triggering of AI scoring for leads.
"""

import structlog
from uuid import UUID
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db_session
from app.models.lead import Lead, LeadStatus
from app.schemas.common import StandardResponse

logger = structlog.get_logger()

router = APIRouter(prefix="/leads", tags=["scoring"])


@router.post("/{lead_id}/score", response_model=StandardResponse, status_code=202)
async def trigger_scoring(
    lead_id: UUID,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
) -> StandardResponse:
    """
    Manually trigger or re-trigger AI scoring for a specific lead.

    Returns 202 Accepted immediately. Scoring happens in the background.
    """
    # Verify lead exists
    result = await session.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalars().first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    logger.info("Manual scoring triggered", lead_id=str(lead_id))

    # Queue background scoring task
    background_tasks.add_task(_run_scoring_workflow, str(lead_id))

    return StandardResponse(
        success=True,
        message="Scoring job queued successfully",
        data={"lead_id": str(lead_id)},
        meta={"status": "queued"},
    )


async def _run_scoring_workflow(lead_id: str) -> None:
    """
    Background task to run the full LangGraph scoring workflow.

    This function will:
    1. Fetch the lead and enriched data
    2. Load scoring criteria configurations
    3. Run the LangGraph agent to generate scores
    4. Validate output with anti-hallucination checks
    5. Calculate composite score
    6. Update lead status and save scores to DB
    """
    logger.info("Running scoring workflow", lead_id=lead_id)
    # TODO: Integrate with LangGraph scoring agent
    # from app.agents.graph import score_lead_async
    # result = await score_lead_async(lead_id)
