"""
Idempotent database seeding.

Populates the default scoring criteria (weights that sum to 1.0) and a set of
realistic sample leads with enrichment data, so a fresh install has something
meaningful to score and display. Safe to run repeatedly: existing rows (matched
by criteria name / lead email) are left untouched.
"""

from __future__ import annotations

import asyncio

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import async_session_factory, init_db
from app.models.criteria import CriteriaConfig
from app.models.lead import Lead, LeadStatus
from app.utils.pii import hash_email

logger = structlog.get_logger(__name__)


DEFAULT_CRITERIA = [
    {
        "name": "icp_fit",
        "display_name": "ICP Fit",
        "weight": 0.30,
        "description": "How well the lead matches our ideal customer profile (industry, size, geography).",
    },
    {
        "name": "buying_intent",
        "display_name": "Buying Intent",
        "weight": 0.25,
        "description": "Observable signals that the lead is actively evaluating a solution.",
    },
    {
        "name": "authority",
        "display_name": "Authority",
        "weight": 0.20,
        "description": "The contact's decision-making power or budget influence.",
    },
    {
        "name": "pain_need",
        "display_name": "Pain / Need",
        "weight": 0.15,
        "description": "Severity and clarity of the business problem we can solve.",
    },
    {
        "name": "timing",
        "display_name": "Timing",
        "weight": 0.10,
        "description": "Urgency and compelling events driving a near-term purchase.",
    },
]


SAMPLE_LEADS = [
    {
        "email": "sarah.chen@nimbusdata.io",
        "first_name": "Sarah",
        "last_name": "Chen",
        "company": "Nimbus Data",
        "company_domain": "nimbusdata.io",
        "job_title": "VP of Engineering",
        "source": "webinar",
        "enriched_data": {
            "company_name": "Nimbus Data",
            "industry": "B2B SaaS",
            "employee_count": 850,
            "annual_revenue": 120_000_000.0,
            "tech_stack": ["Python", "AWS", "Kubernetes", "Snowflake"],
            "recent_funding": {"round": "Series C", "amount": 90_000_000, "date": "2025-02"},
            "headquarters": "San Francisco, CA",
            "linkedin_url": "https://www.linkedin.com/company/nimbusdata",
            "competitors": ["Acme Corp", "Globex"],
            "founded_year": 2016,
        },
    },
    {
        "email": "marcus.webb@finflow.com",
        "first_name": "Marcus",
        "last_name": "Webb",
        "company": "FinFlow",
        "company_domain": "finflow.com",
        "job_title": "Chief Technology Officer",
        "source": "inbound_demo",
        "enriched_data": {
            "company_name": "FinFlow",
            "industry": "FinTech",
            "employee_count": 420,
            "annual_revenue": 65_000_000.0,
            "tech_stack": ["Java", "Azure", "Kafka", "Databricks"],
            "recent_funding": {"round": "Series B", "amount": 45_000_000, "date": "2024-11"},
            "headquarters": "New York, NY",
            "linkedin_url": "https://www.linkedin.com/company/finflow",
            "competitors": ["Initech", "Umbrella"],
            "founded_year": 2018,
        },
    },
    {
        "email": "priya.nair@shieldsec.io",
        "first_name": "Priya",
        "last_name": "Nair",
        "company": "ShieldSec",
        "company_domain": "shieldsec.io",
        "job_title": "Director of Security",
        "source": "content_download",
        "enriched_data": {
            "company_name": "ShieldSec",
            "industry": "Cybersecurity",
            "employee_count": 190,
            "annual_revenue": 28_000_000.0,
            "tech_stack": ["Go", "AWS", "Terraform", "Redis"],
            "recent_funding": {"round": "Series A", "amount": 22_000_000, "date": "2024-06"},
            "headquarters": "Austin, TX",
            "linkedin_url": "https://www.linkedin.com/company/shieldsec",
            "competitors": ["Hooli", "Pied Piper"],
            "founded_year": 2020,
        },
    },
    {
        "email": "tom.baker@localbites.co",
        "first_name": "Tom",
        "last_name": "Baker",
        "company": "LocalBites",
        "company_domain": "localbites.co",
        "job_title": "Marketing Manager",
        "source": "cold_list",
        "enriched_data": {
            "company_name": "LocalBites",
            "industry": "E-commerce",
            "employee_count": 35,
            "annual_revenue": 4_500_000.0,
            "tech_stack": ["Ruby", "Heroku", "Sidekiq", "MySQL"],
            "recent_funding": {"round": "Seed", "amount": 3_000_000, "date": "2022-03"},
            "headquarters": "Toronto, CA",
            "linkedin_url": "https://www.linkedin.com/company/localbites",
            "competitors": ["Vandelay", "Wonka Inc"],
            "founded_year": 2021,
        },
    },
    {
        "email": "elena.rossi@medsync.health",
        "first_name": "Elena",
        "last_name": "Rossi",
        "company": "MedSync",
        "company_domain": "medsync.health",
        "job_title": "Head of Data Platform",
        "source": "partner_referral",
        "enriched_data": {
            "company_name": "MedSync",
            "industry": "Healthcare Technology",
            "employee_count": 610,
            "annual_revenue": 88_000_000.0,
            "tech_stack": ["TypeScript", "GCP", "React", "PostgreSQL"],
            "recent_funding": {"round": "Series C", "amount": 75_000_000, "date": "2025-01"},
            "headquarters": "Boston, MA",
            "linkedin_url": "https://www.linkedin.com/company/medsync",
            "competitors": ["Acme Corp", "Globex"],
            "founded_year": 2015,
        },
    },
]


async def seed_criteria(session: AsyncSession) -> int:
    """Insert any missing default criteria. Returns the number inserted."""
    existing = {
        name
        for (name,) in (
            await session.execute(select(CriteriaConfig.name))
        ).all()
    }
    inserted = 0
    for criterion in DEFAULT_CRITERIA:
        if criterion["name"] in existing:
            continue
        session.add(CriteriaConfig(**criterion, is_active=True))
        inserted += 1
    return inserted


async def seed_leads(session: AsyncSession) -> int:
    """Insert any missing sample leads. Returns the number inserted."""
    existing = {
        email
        for (email,) in (await session.execute(select(Lead.email))).all()
    }
    inserted = 0
    for lead in SAMPLE_LEADS:
        if lead["email"] in existing:
            continue
        session.add(
            Lead(
                email=lead["email"],
                email_hash=hash_email(lead["email"], settings.PII_SALT),
                first_name=lead["first_name"],
                last_name=lead["last_name"],
                company=lead["company"],
                company_domain=lead["company_domain"],
                job_title=lead["job_title"],
                source=lead["source"],
                enriched_data=lead["enriched_data"],
                status=LeadStatus.ENRICHED,
            )
        )
        inserted += 1
    return inserted


async def seed() -> None:
    """Ensure the schema exists, then seed criteria and sample leads."""
    await init_db()
    async with async_session_factory() as session:
        criteria_added = await seed_criteria(session)
        leads_added = await seed_leads(session)
        await session.commit()
    logger.info("Seeding complete", criteria_added=criteria_added, leads_added=leads_added)
    print(f"Seed complete: +{criteria_added} criteria, +{leads_added} leads")


def main() -> None:
    """Synchronous entrypoint for ``python -m app.db.seed`` / scripts."""
    asyncio.run(seed())


if __name__ == "__main__":
    main()
