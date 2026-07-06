"""
SQLAlchemy ORM model for CriteriaConfig entity.

Stores configuration for scoring criteria used in lead evaluation.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Index, String, Text
from app.db.base import PortableUUID as UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CriteriaConfig(Base):
    """
    ORM model for the criteria_configs table.

    Stores the definition and weight of each scoring criterion.
    """

    __tablename__ = "criteria_configs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weight: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0-1.0
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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

    def __repr__(self) -> str:
        """Return string representation of the CriteriaConfig."""
        return f"<CriteriaConfig(id={self.id}, name={self.name}, weight={self.weight})>"
