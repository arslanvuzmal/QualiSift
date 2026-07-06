"""
Deterministic mock enrichment adapter.

Produces realistic, varied firmographic data derived from a hash of the
company domain, so the same domain always yields the same profile. This lets
the whole pipeline run end-to-end with zero external API keys, and makes demos
and tests reproducible.
"""

from __future__ import annotations

import hashlib

from app.adapters.enrichment.base import EnrichedCompanyData, EnrichmentAdapter

_INDUSTRIES = [
    "B2B SaaS",
    "FinTech",
    "Healthcare Technology",
    "E-commerce",
    "Cybersecurity",
    "Logistics & Supply Chain",
    "Marketing Technology",
    "Developer Tools",
]
_TECH = [
    ["Python", "AWS", "Kubernetes", "Snowflake"],
    ["TypeScript", "GCP", "React", "PostgreSQL"],
    ["Java", "Azure", "Kafka", "Databricks"],
    ["Go", "AWS", "Terraform", "Redis"],
    ["Ruby", "Heroku", "Sidekiq", "MySQL"],
]
_HQS = [
    "San Francisco, CA",
    "New York, NY",
    "Austin, TX",
    "Boston, MA",
    "London, UK",
    "Berlin, DE",
    "Toronto, CA",
]
_ROUNDS = ["Seed", "Series A", "Series B", "Series C", "Series D"]
_COMPETITORS = [
    ["Acme Corp", "Globex"],
    ["Initech", "Umbrella"],
    ["Hooli", "Pied Piper"],
    ["Vandelay", "Wonka Inc"],
]


class MockEnrichmentAdapter(EnrichmentAdapter):
    """Returns believable, deterministic enrichment data (no network calls)."""

    name = "mock"

    def _profile(self, domain: str) -> EnrichedCompanyData:
        seed = int(hashlib.sha256(domain.encode("utf-8")).hexdigest(), 16)
        company = domain.split(".")[0].replace("-", " ").title()
        employees = 25 + (seed % 40) * 75  # 25 .. ~3000
        revenue = float(employees) * 185_000.0  # rough ARR-per-head heuristic
        funding_amount = (5 + (seed % 25)) * 5_000_000  # $25M .. $150M
        founded = 2004 + (seed % 20)

        return EnrichedCompanyData(
            company_name=company,
            industry=_INDUSTRIES[seed % len(_INDUSTRIES)],
            employee_count=employees,
            annual_revenue=revenue,
            tech_stack=_TECH[seed % len(_TECH)],
            recent_funding={
                "round": _ROUNDS[seed % len(_ROUNDS)],
                "amount": funding_amount,
                "date": f"{2023 + (seed % 2)}-{1 + (seed % 12):02d}",
            },
            headquarters=_HQS[seed % len(_HQS)],
            linkedin_url=f"https://www.linkedin.com/company/{domain.split('.')[0]}",
            competitors=_COMPETITORS[seed % len(_COMPETITORS)],
            founded_year=founded,
        )

    async def enrich_by_email(self, email: str) -> EnrichedCompanyData:
        return self._profile(self.domain_from_email(email))

    async def enrich_by_domain(self, domain: str) -> EnrichedCompanyData:
        return self._profile(domain.strip().lower())
