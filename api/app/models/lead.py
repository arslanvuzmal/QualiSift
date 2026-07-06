from datetime import datetime, UTC
from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from api.app.db.base import Base

class Lead(Base):
    """
    Lead model representing a potential customer.
    """
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    status: Mapped[str] = mapped_column(String(50), default="new", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), index=True)

    def __repr__(self) -> str:
        return f"<Lead(email='{self.email}', score={self.score})>"
