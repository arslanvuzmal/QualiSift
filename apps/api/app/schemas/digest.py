"""Pydantic schemas for the daily digest system."""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime


class LeadDigestItem(BaseModel):
    """Represents a single lead in the digest."""
    id: str
    email: str
    first_name: str
    last_name: str
    company: str
    job_title: str
    composite_score: float = Field(ge=0, le=100)
    status: str

    # These are optional on a lead (LeadCreate); a missing one used to make the whole digest fail.
    @field_validator("first_name", "last_name", "company", "job_title", mode="before")
    @classmethod
    def _missing_as_empty(cls, v: object) -> object:
        return "" if v is None else v


class HotLeadDigestItem(LeadDigestItem):
    """Extended lead item for hot leads with additional details."""
    overall_summary: str = Field(min_length=30, max_length=500)
    suggested_action: str
    criteria_scores: list[dict]


class WarmLeadDigestItem(LeadDigestItem):
    """Simplified lead item for warm leads."""
    pass


class DigestPayload(BaseModel):
    """Complete payload for daily digest generation."""
    run_date: datetime
    total_leads: int
    hot_count: int
    warm_count: int
    cold_count: int
    hot_leads: list[HotLeadDigestItem] = []
    warm_leads: list[WarmLeadDigestItem] = []
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "run_date": "2025-01-15T00:00:00",
                "total_leads": 10,
                "hot_count": 3,
                "warm_count": 4,
                "cold_count": 3
            }
        }
    )
