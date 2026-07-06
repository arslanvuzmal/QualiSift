"""
SQLAlchemy ORM model for Lead entity.

Represents a sales lead with contact information, company data, and status tracking.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, String, Text
from app.db.base import JSONType as JSONB, PortableUUID as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.score import Score, CompositeScore


class LeadStatus(str, PyEnum):
    """Enumeration of possible lead statuses."""

    NEW = "new"
    ENRICHED = "enriched"
    SCORED = "scored"
    DIGESTED = "digested"
    DISQUALIFIED = "disqualified"


class Lead(Base):
    """
    ORM model for the leads table.

    Stores information about potential sales leads including contact details,
    company information, and enrichment data.
    """

    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company_domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    enriched_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus),
        default=LeadStatus.NEW,
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    scores: Mapped[list["Score"]] = relationship(
        "Score",
        back_populates="lead",
        cascade="all, delete-orphan",
    )
    composite_score: Mapped[Optional["CompositeScore"]] = relationship(
        "CompositeScore",
        back_populates="lead",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Table indexes
    __table_args__ = (
        Index("ix_leads_company_domain_status", "company_domain", "status"),
    )

    def __repr__(self) -> str:
        """Return string representation of the Lead."""
        return f"<Lead(id={self.id}, email={self.email}, company={self.company})>"
