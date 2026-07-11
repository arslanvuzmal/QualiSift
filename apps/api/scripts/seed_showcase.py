"""
Idempotent script to seed the database with showcase data.
Populates 100+ realistic leads, their scores, composite scores, and 30 days of digest runs.

Run with: python -m scripts.seed_showcase
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import async_session_factory, init_db
from app.models.lead import Lead, LeadStatus
from app.models.score import Score, CompositeScore
from app.models.digest import DigestRun, DigestStatus
from app.utils.pii import hash_email

logger = structlog.get_logger(__name__)

COMPANIES = [
    ("Nexus AI", "nexus.ai", "SaaS", 150),
    ("Vertex SaaS", "vertex.io", "Enterprise Software", 800),
    ("Quantum Logistics", "quantumlogistics.com", "Logistics", 1200),
    ("FinFlow", "finflow.finance", "FinTech", 400),
    ("ShieldSec", "shieldsec.io", "Cybersecurity", 250),
    ("HealthSync", "healthsync.io", "HealthTech", 600),
    ("DataSphere", "datasphere.net", "Data Analytics", 300),
    ("CloudScale", "cloudscale.com", "Cloud Infrastructure", 1500),
    ("InnovateXR", "innovatexr.com", "VR/AR", 90),
    ("EcoSolutions", "ecosolutions.org", "CleanTech", 200),
    ("AutoDrive", "autodrive.ai", "Automotive", 5000),
    ("RetailEdge", "retailedge.com", "E-commerce", 450),
    ("BioGenetics", "biogen.med", "Biotech", 800),
    ("AeroDynamics", "aerodynamics.com", "Aerospace", 3000),
    ("EduTech Innovators", "edutechi.com", "EdTech", 120),
    ("Global Payments", "globalpay.net", "FinTech", 2500),
    ("NextGen Robotics", "nextgenrobotics.com", "Hardware", 400),
    ("Urban Mobility", "urbanmob.city", "Transportation", 350),
    ("AgriTech Solutions", "agritech.farm", "Agriculture", 180),
    ("SmartHome Devices", "smarthome.net", "IoT", 600)
]

FIRST_NAMES = ["Sarah", "Marcus", "Priya", "Tom", "Elena", "David", "Jessica", "Michael", "Sophia", "James", "Emma", "William", "Olivia", "Alexander", "Ava"]
LAST_NAMES = ["Chen", "Webb", "Nair", "Baker", "Rossi", "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
JOB_TITLES = ["VP of Engineering", "Head of Revenue", "Chief Technology Officer", "Director of Security", "Marketing Manager", "Head of Data Platform", "CEO", "COO", "VP of Sales", "Product Manager"]
SOURCES = ["webinar", "inbound_demo", "content_download", "cold_list", "partner_referral", "event_lead"]

CRITERIA = ["icp_fit", "buying_intent", "authority", "pain_need", "timing"]

async def seed_leads_and_scores(session: AsyncSession) -> int:
    existing_emails = {
        email for (email,) in (await session.execute(select(Lead.email))).all()
    }
    
    inserted = 0
    now = datetime.utcnow()
    
    for _ in range(100):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        company_name, company_domain, industry, emp_count = random.choice(COMPANIES)
        email = f"{first_name.lower()}.{last_name.lower()}@{company_domain}"
        
        if email in existing_emails:
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 9999)}@{company_domain}"
            if email in existing_emails:
                continue
                
        existing_emails.add(email)
        
        lead_id = uuid.uuid4()
        lead = Lead(
            id=lead_id,
            email=email,
            email_hash=hash_email(email, settings.PII_SALT),
            first_name=first_name,
            last_name=last_name,
            company=company_name,
            company_domain=company_domain,
            job_title=random.choice(JOB_TITLES),
            source=random.choice(SOURCES),
            enriched_data={
                "company_name": company_name,
                "industry": industry,
                "employee_count": emp_count,
                "headquarters": "San Francisco, CA" if random.random() > 0.5 else "New York, NY",
                "annual_revenue": emp_count * 100000,
            },
            status=LeadStatus.SCORED,
            created_at=now - timedelta(days=random.randint(0, 30)),
            updated_at=now
        )
        session.add(lead)
        
        composite_val = 0.0
        for crit in CRITERIA:
            if random.random() > 0.8:
                score_val = random.randint(8, 10)
            elif random.random() > 0.4:
                score_val = random.randint(4, 7)
            else:
                score_val = random.randint(1, 3)
                
            session.add(Score(
                id=uuid.uuid4(),
                lead_id=lead_id,
                criteria_name=crit,
                score=score_val,
                reasoning=f"Based on their profile and activity, {crit} is scored at {score_val}/10.",
                confidence=random.uniform(0.7, 0.99)
            ))
            composite_val += score_val
            
        comp_score = (composite_val / 50.0) * 100.0
        
        summary = "Average prospect."
        action = "Nurture via email."
        if comp_score >= 75:
            summary = "High-value enterprise prospect with strong fit."
            action = "Assign to enterprise AE immediately."
        elif comp_score < 40:
            summary = "Low fit, unlikely to convert."
            action = "Disqualify."
            
        session.add(CompositeScore(
            id=uuid.uuid4(),
            lead_id=lead_id,
            composite_score=comp_score,
            overall_summary=summary,
            suggested_action=action,
            disqualify=comp_score < 40
        ))
        
        inserted += 1
        
    return inserted

async def seed_digest_runs(session: AsyncSession):
    existing_dates = {
        d.date() for (d,) in (await session.execute(select(DigestRun.run_date))).all()
    }
    
    today = datetime.utcnow()
    inserted = 0
    
    for i in range(30):
        run_date = today - timedelta(days=i)
        
        if run_date.date() in existing_dates:
            continue
            
        base_leads = 10 + (30 - i) * 2 + random.randint(-5, 5)
        base_leads = max(5, base_leads)
        
        hot = int(base_leads * random.uniform(0.1, 0.3))
        warm = int(base_leads * random.uniform(0.3, 0.5))
        cold = base_leads - hot - warm
        
        session.add(DigestRun(
            id=uuid.uuid4(),
            run_date=run_date,
            total_leads=base_leads,
            hot_count=hot,
            warm_count=warm,
            cold_count=cold,
            status=DigestStatus.SENT,
            created_at=run_date
        ))
        inserted += 1
        
    return inserted

async def seed() -> None:
    await init_db()
    async with async_session_factory() as session:
        leads_added = await seed_leads_and_scores(session)
        digests_added = await seed_digest_runs(session)
        await session.commit()
    print(f"Showcase seeding complete: {leads_added} leads and {digests_added} days of history generated.")

def main() -> None:
    asyncio.run(seed())

if __name__ == "__main__":
    main()
