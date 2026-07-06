"""
Schemas package for the AI Sales Lead Qualifier API.

This module exports all Pydantic schemas for easy importing.
"""

from app.schemas.common import StandardResponse
from app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadRead,
    LeadListResponse,
    CriteriaScoreRead,
    CompositeScoreRead,
)
from app.schemas.score import ScoreLeadRequest
from app.schemas.criteria import CriteriaConfigRead, CriteriaConfigUpdate

__all__ = [
    "StandardResponse",
    "LeadCreate",
    "LeadUpdate",
    "LeadRead",
    "LeadListResponse",
    "CriteriaScoreRead",
    "CompositeScoreRead",
    "ScoreLeadRequest",
    "CriteriaConfigRead",
    "CriteriaConfigUpdate",
]
