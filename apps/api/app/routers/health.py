"""
FastAPI router for Health and Status endpoints.

Checks database, Redis, and overall system health.
"""

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.db.session import get_db_session
from app.schemas.common import StandardResponse

logger = structlog.get_logger()

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=StandardResponse)
async def health_check(
    session: AsyncSession = Depends(get_db_session),
) -> StandardResponse:
    """
    Comprehensive health check for the API.

    Checks:
    - Database connectivity
    - Redis connectivity (if configured)
    - Overall API status
    """
    health_status = {
        "api": "ok",
        "database": "unknown",
        "redis": "unknown",
    }

    # Check database
    try:
        result = await session.execute(text("SELECT 1"))
        result.fetchone()
        health_status["database"] = "ok"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        health_status["database"] = "error"

    # Check Redis (optional)
    try:
        from app.config import settings
        import redis.asyncio as redis

        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()
        health_status["redis"] = "ok"
    except Exception as e:
        logger.warning("Redis health check failed or not configured", error=str(e))
        health_status["redis"] = "unavailable"

    # Determine overall status
    all_healthy = all(v == "ok" for v in health_status.values())
    any_critical = health_status.get("database") == "error"

    if any_critical:
        overall_status = "unhealthy"
        status_code = 503
    elif not all_healthy:
        overall_status = "degraded"
        status_code = 200
    else:
        overall_status = "healthy"
        status_code = 200

    return StandardResponse(
        success=all_healthy,
        data={
            "status": overall_status,
            "checks": health_status,
        },
        meta={"version": "0.1.0"},
    )


@router.get("/ready", response_model=StandardResponse)
async def readiness_check(
    session: AsyncSession = Depends(get_db_session),
) -> StandardResponse:
    """
    Readiness probe for Kubernetes/load balancers.

    Returns 200 only if the service is ready to accept traffic.
    """
    try:
        # Quick database check
        result = await session.execute(text("SELECT 1"))
        result.fetchone()
        return StandardResponse(
            success=True,
            data={"ready": True},
        )
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        return StandardResponse(
            success=False,
            data={"ready": False, "error": str(e)},
        )
