"""
FastAPI router for Criteria Configuration endpoints.

Handles viewing and updating scoring criteria weights and descriptions.
"""

import structlog
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db_session
from app.models.criteria import CriteriaConfig
from app.schemas.criteria import CriteriaConfigRead, CriteriaConfigUpdate
from app.schemas.common import StandardResponse

logger = structlog.get_logger()

router = APIRouter(prefix="/criteria", tags=["criteria"])


@router.get("", response_model=StandardResponse)
async def list_criteria(
    active_only: bool = True,
    session: AsyncSession = Depends(get_db_session),
) -> StandardResponse:
    """
    List all scoring criteria configurations.
    """
    query = select(CriteriaConfig)
    if active_only:
        query = query.where(CriteriaConfig.is_active == True)

    result = await session.execute(query)
    criteria = result.scalars().all()

    items = [
        CriteriaConfigRead(
            id=c.id,
            name=c.name,
            display_name=c.display_name,
            description=c.description,
            weight=c.weight,
            is_active=c.is_active,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in criteria
    ]

    return StandardResponse(
        success=True,
        data=items,
        meta={"count": len(items)},
    )


@router.get("/{criteria_id}", response_model=StandardResponse)
async def get_criteria(
    criteria_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> StandardResponse:
    """
    Get a specific criteria configuration by ID.
    """
    result = await session.execute(
        select(CriteriaConfig).where(CriteriaConfig.id == criteria_id)
    )
    criteria = result.scalars().first()

    if not criteria:
        raise HTTPException(status_code=404, detail="Criteria not found")

    return StandardResponse(
        success=True,
        data=CriteriaConfigRead(
            id=criteria.id,
            name=criteria.name,
            display_name=criteria.display_name,
            description=criteria.description,
            weight=criteria.weight,
            is_active=criteria.is_active,
            created_at=criteria.created_at,
            updated_at=criteria.updated_at,
        ),
    )


@router.put("/{criteria_id}", response_model=StandardResponse)
async def update_criteria(
    criteria_id: UUID,
    update_data: CriteriaConfigUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> StandardResponse:
    """
    Update a criteria configuration (weight, description, etc.).
    """
    result = await session.execute(
        select(CriteriaConfig).where(CriteriaConfig.id == criteria_id)
    )
    criteria = result.scalars().first()

    if not criteria:
        raise HTTPException(status_code=404, detail="Criteria not found")

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(criteria, field, value)

    await session.commit()
    await session.refresh(criteria)

    logger.info("Criteria updated", criteria_id=str(criteria_id), updates=update_dict)

    return StandardResponse(
        success=True,
        message="Criteria updated successfully",
        data=CriteriaConfigRead(
            id=criteria.id,
            name=criteria.name,
            display_name=criteria.display_name,
            description=criteria.description,
            weight=criteria.weight,
            is_active=criteria.is_active,
            created_at=criteria.created_at,
            updated_at=criteria.updated_at,
        ),
    )
