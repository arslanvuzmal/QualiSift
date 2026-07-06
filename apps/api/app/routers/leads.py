"""
FastAPI router for Lead management endpoints.

Handles CRUD operations for leads and triggers background scoring.
"""

import structlog
from uuid import UUID
from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.session import get_db_session
from app.models.lead import Lead, LeadStatus
from app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadRead,
    LeadListResponse,
)
from app.schemas.common import StandardResponse
from app.services.digest import DigestService

logger = structlog.get_logger()

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=StandardResponse, status_code=202)
async def create_lead(
    lead_data: LeadCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
) -> StandardResponse:
    """
    Create a new lead and queue it for AI scoring.

    Returns 202 Accepted immediately. Scoring happens in the background.
    """
    # Check if lead already exists
    existing = await session.execute(
        select(Lead).where(Lead.email == lead_data.email)
    )
    existing_lead = existing.scalars().first()

    if existing_lead:
        raise HTTPException(
            status_code=409,
            detail=f"Lead with email {lead_data.email} already exists",
        )

    # Create new lead
    from app.utils.pii import hash_email

    new_lead = Lead(
        email=lead_data.email,
        email_hash=hash_email(lead_data.email, "default-salt"),
        first_name=lead_data.first_name,
        last_name=lead_data.last_name,
        company=lead_data.company,
        company_domain=lead_data.company_domain,
        job_title=lead_data.job_title,
        source=lead_data.source or "api",
        raw_payload=lead_data.raw_payload or {},
        status=LeadStatus.NEW,
    )

    session.add(new_lead)
    await session.commit()
    await session.refresh(new_lead)

    logger.info("Lead created", lead_id=str(new_lead.id), email=new_lead.email)

    # Queue background scoring task
    background_tasks.add_task(_trigger_scoring, str(new_lead.id))

    return StandardResponse(
        success=True,
        message="Lead accepted and queued for scoring",
        data={"lead_id": str(new_lead.id)},
        meta={"status": "queued"},
    )


async def _trigger_scoring(lead_id: str) -> None:
    """Background task: enrich + score a newly created lead and persist results."""
    logger.info("Triggering scoring for lead", lead_id=lead_id)
    from app.services.scoring import score_lead_by_id

    try:
        await score_lead_by_id(lead_id)
    except Exception as exc:  # noqa: BLE001 - background task must not crash silently
        logger.exception("Background scoring failed", lead_id=lead_id, error=str(exc))


@router.get("", response_model=StandardResponse)
async def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: LeadStatus | None = None,
    company_domain: str | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> StandardResponse:
    """
    List leads with pagination and filtering.
    """
    # Build query
    query = select(Lead)

    if status:
        query = query.where(Lead.status == status)
    if company_domain:
        query = query.where(Lead.company_domain == company_domain)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination (eager-load scores + composite so the list can show them)
    offset = (page - 1) * page_size
    query = (
        query.offset(offset)
        .limit(page_size)
        .options(selectinload(Lead.scores), selectinload(Lead.composite_score))
    )

    result = await session.execute(query)
    leads = result.scalars().all()

    items = [LeadRead.model_validate(lead) for lead in leads]

    return StandardResponse(
        success=True,
        data=LeadListResponse(items=items, total=total, page=page, page_size=page_size),
        meta={"page": page, "page_size": page_size, "total_pages": (total + page_size - 1) // page_size},
    )


@router.get("/{lead_id}", response_model=StandardResponse)
async def get_lead(
    lead_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> StandardResponse:
    """
    Get a specific lead by ID with nested scores.
    """
    result = await session.execute(
        select(Lead)
        .where(Lead.id == lead_id)
        .options(selectinload(Lead.scores), selectinload(Lead.composite_score))
    )
    lead = result.scalars().first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return StandardResponse(success=True, data=LeadRead.model_validate(lead))
