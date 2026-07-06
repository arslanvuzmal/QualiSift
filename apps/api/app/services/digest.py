"""Daily digest compilation service."""

import structlog
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.lead import Lead
from app.models.score import CompositeScore
from app.schemas.digest import DigestPayload, HotLeadDigestItem, WarmLeadDigestItem

logger = structlog.get_logger()


class DigestService:
    """Service for compiling daily lead digests."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def compile_digest(self, run_date: Optional[datetime] = None) -> DigestPayload:
        """
        Compile the daily digest for leads scored in the last 24 hours.
        
        Args:
            run_date: The date for which to compile the digest. Defaults to now.
            
        Returns:
            DigestPayload containing segmented leads and statistics.
        """
        if run_date is None:
            run_date = datetime.now(timezone.utc)
        
        # Calculate the time window (last 24 hours)
        cutoff_time = run_date - timedelta(hours=24)
        
        logger.info("Compiling daily digest", run_date=run_date.isoformat(), cutoff=cutoff_time.isoformat())
        
        # Query for scored leads in the last 24 hours
        query = select(Lead).join(CompositeScore).where(
            and_(
                Lead.status == 'scored',
                Lead.created_at >= cutoff_time
            )
        )
        
        result = await self.db.execute(query)
        leads = result.scalars().all()
        
        # Segment leads by composite score
        hot_leads = []
        warm_leads = []
        cold_count = 0
        
        for lead in leads:
            # Get composite score for this lead
            score_query = select(CompositeScore).where(CompositeScore.lead_id == lead.id)
            score_result = await self.db.execute(score_query)
            composite = score_result.scalars().first()
            
            if not composite:
                continue
            
            lead_data = {
                "id": str(lead.id),
                "email": lead.email,
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "company": lead.company,
                "job_title": lead.job_title,
                "composite_score": composite.composite_score,
                "status": lead.status,
            }
            
            # Segment by score
            if composite.composite_score >= 75:
                # Hot lead - include full details
                hot_lead = HotLeadDigestItem(
                    **lead_data,
                    overall_summary=composite.overall_summary,
                    suggested_action=composite.suggested_action,
                    criteria_scores=[
                        {
                            "criteria_name": s.criteria_name,
                            "score": s.score,
                            "reasoning": s.reasoning,
                            "confidence": s.confidence
                        }
                        for s in lead.scores
                    ] if hasattr(lead, 'scores') else []
                )
                hot_leads.append(hot_lead)
            elif composite.composite_score >= 40:
                # Warm lead - include summary only
                warm_lead = WarmLeadDigestItem(**lead_data)
                warm_leads.append(warm_lead)
            else:
                # Cold lead - count only
                cold_count += 1
        
        payload = DigestPayload(
            run_date=run_date,
            total_leads=len(leads),
            hot_count=len(hot_leads),
            warm_count=len(warm_leads),
            cold_count=cold_count,
            hot_leads=hot_leads,
            warm_leads=warm_leads
        )
        
        logger.info(
            "Digest compiled successfully",
            total=payload.total_leads,
            hot=payload.hot_count,
            warm=payload.warm_count,
            cold=payload.cold_count
        )
        
        return payload
