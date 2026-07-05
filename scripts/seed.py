"""
Database seed script for AI Sales Lead Qualifier.

This script connects to the database, creates all tables, and populates
with dummy data for development purposes.
"""

import asyncio
import sys
from pathlib import Path

# Add the api directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.config import get_settings


async def seed_database() -> None:
    """
    Initialize the database by creating all tables.
    
    This is a placeholder script that will be expanded in Phase 2
    to include actual dummy data population.
    """
    settings = get_settings()
    
    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=True,
    )
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database seeded successfully")
        print("   - All tables created")
        print("   - Note: Actual dummy data will be added in Phase 2")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
