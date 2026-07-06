"""
Pydantic schemas for Lead API request/response validation.

These schemas define the structure of data exchanged via the API.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.lead import LeadStatus


class LeadCreate(BaseModel):
    """Schema for creating a new lead."""

    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=255)
    company_domain: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)
    source: Optional[str] = Field(None, max_length=100)
    raw_payload: Optional[dict[str, Any]] = None


class LeadUpdate(BaseModel):
    """Schema for updating an existing lead."""

    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=255)
    company_domain: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)
    status: Optional[LeadStatus] = None
    enriched_data: Optional[dict[str, Any]] = None


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


class LeadRead(BaseModel):
    """Schema for reading lead data with nested scores."""

    id: UUID
    email: str
    email_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    company_domain: Optional[str] = None
    job_title: Optional[str] = None
    source: Optional[str] = None
    raw_payload: Optional[dict[str, Any]] = None
    enriched_data: Optional[dict[str, Any]] = None
    status: LeadStatus
    created_at: datetime
    updated_at: datetime
    scores: Optional[list[CriteriaScoreRead]] = None
    composite_score: Optional[CompositeScoreRead] = None

    model_config = ConfigDict(from_attributes=True)


class LeadListResponse(BaseModel):
    """Schema for paginated lead list responses."""

    items: list[LeadRead]
    total: int
    page: int = 1
    page_size: int = 20

    model_config = ConfigDict(from_attributes=True)
