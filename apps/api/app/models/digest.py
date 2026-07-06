"""
SQLAlchemy ORM model for DigestRun entity.

Stores records of daily/weekly digest runs that summarize lead status.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import DateTime, Enum, Integer, Text
from app.db.base import PortableUUID as UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DigestStatus(str, PyEnum):
    """Enumeration of possible digest run statuses."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class DigestRun(Base):
    """
    ORM model for the digest_runs table.

    Stores information about automated digest emails/reports sent to sales teams.
    """

    __tablename__ = "digest_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    run_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        index=True,
    )
    total_leads: Mapped[int] = mapped_column(Integer, nullable=False)
    hot_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    warm_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cold_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    email_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    slack_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    status: Mapped[DigestStatus] = mapped_column(
        Enum(DigestStatus),
        default=DigestStatus.PENDING,
        nullable=False,
        index=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return string representation of the DigestRun."""
        return f"<DigestRun(id={self.id}, run_date={self.run_date}, status={self.status})>"
