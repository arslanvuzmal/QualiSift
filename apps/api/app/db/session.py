"""
Database session and engine configuration.

This module provides async SQLAlchemy engine and session factory
for database operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session

from app.config import settings


def get_async_engine() -> any:
    """
    Create and return an async SQLAlchemy engine.

    Returns:
        AsyncEngine: SQLAlchemy async engine instance.
    """
    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


# Global engine instance
async_engine = get_async_engine()


# Session factory for dependency injection
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncSession:
    """
    Dependency generator for database sessions.

    Yields:
        AsyncSession: Database session for request handling.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session() -> Session:
    """
    Get a synchronous session for scripts and migrations.

    Returns:
        Session: Synchronous database session.
    """
    # Create sync engine from async URL
    sync_url = str(settings.DATABASE_URL).replace(
        "postgresql+asyncpg", "postgresql"
    )
    sync_engine = create_async_engine(
        sync_url.replace("+asyncpg", ""),
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )
    return Session(bind=sync_engine)
