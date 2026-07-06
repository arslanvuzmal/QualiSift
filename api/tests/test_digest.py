import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from api.app.db.base import Base
from api.app.models.lead import Lead
from api.app.services.digest import DigestService

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def db_session():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    await engine.dispose()

@pytest.mark.asyncio
async def test_compile_daily_digest(db_session):
    # Add test data
    leads = [
        Lead(name="Hot", email="hot@test.com", score=0.9),
        Lead(name="Warm", email="warm@test.com", score=0.6),
        Lead(name="Cold", email="cold@test.com", score=0.2),
    ]
    db_session.add_all(leads)
    await db_session.commit()

    service = DigestService(db_session)
    digest = await service.compile_daily_digest()

    assert len(digest["hot"]) == 1
    assert len(digest["warm"]) == 1
    assert len(digest["cold"]) == 1
    assert digest["hot"][0].name == "Hot"
