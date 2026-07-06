import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from api.app.config import get_settings
from api.app.logging import logger

async def run_diagnostics():
    """
    Enterprise-level diagnostics for Cortex system.
    """
    logger.info("--- Starting System Diagnostics ---")
    settings = get_settings()

    # 1. Database Connectivity
    logger.info(f"Checking Database: {settings.database_url}")
    try:
        engine = create_async_engine(settings.database_url)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database Connection: SUCCESS")
    except Exception as e:
        logger.error(f"❌ Database Connection: FAILED - {str(e)}")
    finally:
        await engine.dispose()

    # 2. Environment Variables
    required_vars = ["DATABASE_URL"]
    for var in required_vars:
        if os.getenv(var):
            logger.info(f"✅ Environment Var {var}: SET")
        else:
            logger.warning(f"⚠️ Environment Var {var}: NOT SET (Using default)")

    # 3. Directory Structure
    dirs = ["api/app/models", "api/app/services", "api/app/adapters"]
    for d in dirs:
        if Path(d).is_dir():
            logger.info(f"✅ Directory {d}: EXISTS")
        else:
            logger.error(f"❌ Directory {d}: MISSING")

    logger.info("--- Diagnostics Complete ---")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
