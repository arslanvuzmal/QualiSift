"""
Pydantic schemas for Score API request/response validation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CriteriaScoreRead(BaseModel):
    """Schema for reading individual criterion scores."""

    id: UUID
    criteria_name: str
    score: int = Field(ge=1, le=10)
    reasoning: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompositeScoreRead(BaseModel):
    """Schema for reading composite scores."""

    id: UUID
    composite_score: float = Field(ge=0.0, le=100.0)
    overall_summary: Optional[str] = None
    suggested_action: Optional[str] = None
    disqualify: bool
    disqualify_reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScoreLeadRequest(BaseModel):
    """Schema for requesting lead scoring."""

    lead_id: UUID
    criteria_override: Optional[dict[str, float]] = None

    model_config = ConfigDict(from_attributes=True)
