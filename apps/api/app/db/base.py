"""
SQLAlchemy declarative base for database models.

All ORM models should inherit from this Base class.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Declarative base class for all SQLAlchemy models.

    This base class provides common functionality and metadata
    for all database models in the application.
    """

    pass
