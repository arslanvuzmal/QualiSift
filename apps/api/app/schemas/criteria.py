"""
Pydantic schemas for CriteriaConfig API request/response validation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CriteriaConfigRead(BaseModel):
    """Schema for reading criteria configuration."""

    id: UUID
    name: str
    display_name: str
    description: Optional[str] = None
    weight: float = Field(ge=0.0, le=1.0)
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CriteriaConfigUpdate(BaseModel):
    """Schema for updating criteria configuration."""

    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)
