"""
Database session and engine configuration.

Provides an async SQLAlchemy engine, a session factory for FastAPI dependency
injection, and a helper to create tables for local development / tests.

The engine is dialect-aware: PostgreSQL gets a connection pool, while SQLite
(used for Postgres-less local dev and CI) omits the unsupported pool options.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


def _engine_kwargs() -> dict:
    """Build engine kwargs appropriate for the configured database dialect."""
    kwargs: dict = {"echo": settings.DEBUG, "pool_pre_ping": True}
    # SQLite does not support the QueuePool sizing options below.
    if not settings.DATABASE_URL.startswith("sqlite"):
        kwargs.update(pool_size=10, max_overflow=20)
    return kwargs


def get_async_engine():
    """Create and return an async SQLAlchemy engine for the configured DB."""
    return create_async_engine(settings.DATABASE_URL, **_engine_kwargs())


# Global engine + session factory
async_engine = get_async_engine()

async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session():
    """FastAPI dependency that yields a transactional async DB session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create any missing tables.

    Used for local development and tests, where Alembic migrations are not
    run. Production creates its schema via ``alembic upgrade head``.
    """
    from app.db.base import Base
    import app.models  # noqa: F401 - ensure every model is registered on Base

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
