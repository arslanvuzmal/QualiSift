"""
Models package for the AI Sales Lead Qualifier API.

This module exports all SQLAlchemy ORM models for easy importing.
"""

from app.db.base import Base
from app.models.lead import Lead, LeadStatus
from app.models.score import Score, CompositeScore
from app.models.criteria import CriteriaConfig
from app.models.digest import DigestRun, DigestStatus
from app.models.config import AppConfig

__all__ = [
    "Base",
    "Lead",
    "LeadStatus",
    "Score",
    "CompositeScore",
    "CriteriaConfig",
    "DigestRun",
    "DigestStatus",
    "AppConfig",
]
