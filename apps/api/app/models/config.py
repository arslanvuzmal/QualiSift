"""
SQLAlchemy ORM model for AppConfig entity.

Stores application configuration key-value pairs with optional encryption.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AppConfig(Base):
    """
    ORM model for the app_config table.

    Stores application configuration as key-value pairs.
    Values can be optionally encrypted for sensitive data.
    """

    __tablename__ = "app_config"

    key: Mapped[str] = mapped_column(String(255), primary_key=True, unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return string representation of the AppConfig."""
        return f"<AppConfig(key={self.key}, is_encrypted={self.is_encrypted})>"
