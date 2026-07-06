from datetime import datetime, timedelta, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.app.models.lead import Lead

class DigestService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def compile_daily_digest(self):
        """
        Query scored leads from last 24 hours and segment them into Hot/Warm/Cold categories.
        """
        yesterday = datetime.now(UTC) - timedelta(days=1)

        query = select(Lead).where(Lead.created_at >= yesterday)
        result = await self.session.execute(query)
        leads = result.scalars().all()

        digest = {
            "hot": [l for l in leads if l.score >= 0.8],
            "warm": [l for l in leads if 0.5 <= l.score < 0.8],
            "cold": [l for l in leads if l.score < 0.5],
            "timestamp": datetime.now(UTC)
        }

        return digest
