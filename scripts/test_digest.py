import asyncio
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from api.app.config import get_settings
from api.app.services.digest import DigestService
from api.app.adapters.notifications.base import ConsoleAdapter

async def test_digest_generation():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 1. Compile Digest
        service = DigestService(session)
        digest = await service.compile_daily_digest()

        # 2. Format Message
        message = f"Daily Lead Digest ({digest['timestamp'].strftime('%Y-%m-%d')})\n"
        message += f"Hot Leads: {len(digest['hot'])}\n"
        for l in digest['hot']:
            message += f" - {l.name} ({l.score})\n"

        message += f"Warm Leads: {len(digest['warm'])}\n"
        message += f"Cold Leads: {len(digest['cold'])}\n"

        # 3. Send via Console Adapter
        adapter = ConsoleAdapter()
        await adapter.send(message, subject="Your Daily Lead Digest")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_digest_generation())
