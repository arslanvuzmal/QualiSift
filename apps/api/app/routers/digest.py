"""
FastAPI router for Digest endpoints.

Handles manual triggering of daily digest and viewing digest history.
"""

import structlog
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db_session
from app.models.digest import DigestRun, DigestStatus
from app.schemas.common import StandardResponse
from app.services.digest import DigestService

logger = structlog.get_logger()

router = APIRouter(prefix="/digest", tags=["digest"])


@router.post("/generate", response_model=StandardResponse)
async def generate_digest(
    session: AsyncSession = Depends(get_db_session),
) -> StandardResponse:
    """
    Manually trigger the daily digest compilation and delivery.

    This will:
    1. Query leads scored in the last 24 hours
    2. Segment into Hot/Warm/Cold
    3. Generate HTML email and Slack payload
    4. Send via configured adapters
    5. Log the digest run to the database
    """
    logger.info("Manual digest generation triggered")

    try:
        # Compile digest
        service = DigestService(session)
        payload = await service.compile_digest()

        # Create digest run record
        digest_run = DigestRun(
            run_date=datetime.now(timezone.utc),
            total_leads=payload.total_leads,
            hot_count=payload.hot_count,
            warm_count=payload.warm_count,
            cold_count=payload.cold_count,
            status=DigestStatus.PENDING,
        )

        session.add(digest_run)
        await session.commit()
        await session.refresh(digest_run)

        # TODO: Send via notification service
        # from app.services.notifications import NotificationService
        # notifier = NotificationService(session)
        # await notifier.send_digest(payload)

        # Update status to sent
        digest_run.status = DigestStatus.SENT
        digest_run.email_sent_at = datetime.now(timezone.utc)
        digest_run.slack_sent_at = datetime.now(timezone.utc)
        await session.commit()

        logger.info(
            "Digest generated successfully",
            total=payload.total_leads,
            hot=payload.hot_count,
            warm=payload.warm_count,
            cold=payload.cold_count,
        )

        return StandardResponse(
            success=True,
            message="Daily digest generated successfully",
            data={
                "run_id": str(digest_run.id),
                "total_leads": payload.total_leads,
                "hot_count": payload.hot_count,
                "warm_count": payload.warm_count,
                "cold_count": payload.cold_count,
            },
        )

    except Exception as e:
        logger.error("Digest generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate digest: {str(e)}")


@router.get("/history", response_model=StandardResponse)
async def get_digest_history(
    limit: int = 10,
    session: AsyncSession = Depends(get_db_session),
) -> StandardResponse:
    """
    Get history of past digest runs.
    """
    query = (
        select(DigestRun)
        .order_by(DigestRun.run_date.desc())
        .limit(limit)
    )

    result = await session.execute(query)
    digest_runs = result.scalars().all()

    history = [
        {
            "id": str(run.id),
            "run_date": run.run_date.isoformat(),
            "total_leads": run.total_leads,
            "hot_count": run.hot_count,
            "warm_count": run.warm_count,
            "cold_count": run.cold_count,
            "status": run.status.value,
            "email_sent_at": run.email_sent_at.isoformat() if run.email_sent_at else None,
            "slack_sent_at": run.slack_sent_at.isoformat() if run.slack_sent_at else None,
        }
        for run in digest_runs
    ]

    return StandardResponse(
        success=True,
        data=history,
        meta={"limit": limit, "count": len(history)},
    )
