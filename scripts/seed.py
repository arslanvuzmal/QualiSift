"""
Database seed script for AI Sales Lead Qualifier.

This script connects to the database, creates all tables, and populates
with dummy data for development purposes.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, UTC

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from api.app.db.base import Base
from api.app.config import get_settings
from api.app.models.lead import Lead


async def seed_database() -> None:
    """
    Initialize the database by creating all tables and adding dummy data.
    """
    settings = get_settings()
    
    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=True,
    )
    
    # Create session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    try:
        # Create all tables
        async with engine.begin() as conn:
            # For SQLite, we might want to drop first for a clean seed
            if "sqlite" in settings.database_url:
                await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        
        # Add dummy data
        async with async_session() as session:
            dummy_leads = [
                Lead(name="John Doe", email="john@example.com", score=0.9, status="hot"),
                Lead(name="Jane Smith", email="jane@example.com", score=0.6, status="warm"),
                Lead(name="Bob Wilson", email="bob@example.com", score=0.2, status="cold"),
                Lead(name="Alice Brown", email="alice@example.com", score=0.85, status="hot"),
            ]

            session.add_all(dummy_leads)
            await session.commit()

        print("✅ Database seeded successfully")
        print(f"   - Database: {settings.database_url}")
        print("   - All tables created")
        print("   - Dummy leads added")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
