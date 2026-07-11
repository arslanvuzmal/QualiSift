"""
Enrichment adapter interface and the enriched-company data contract.

Adapters take a lead's email/domain and return firmographic data used by the
scoring agent. Swapping providers (mock, Clearbit, Apollo, ...) is a config
change, never a code change in the scoring pipeline.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class EnrichedCompanyData(BaseModel):
    """Normalized firmographic data returned by every enrichment provider."""

    company_name: str | None = None
    industry: str | None = None
    employee_count: int | None = None
    annual_revenue: float | None = None
    tech_stack: list[str] = Field(default_factory=list)
    recent_funding: dict | None = None
    headquarters: str | None = None
    linkedin_url: str | None = None
    competitors: list[str] = Field(default_factory=list)
    founded_year: int | None = None


class EnrichmentAdapter(ABC):
    """Abstract base class for company/lead enrichment providers."""

    name: str = "base"

    @abstractmethod
    async def enrich_by_email(self, email: str) -> EnrichedCompanyData:
        """Enrich a lead using their email address (domain is derived)."""

    @abstractmethod
    async def enrich_by_domain(self, domain: str) -> EnrichedCompanyData:
        """Enrich a company using its web domain."""

    @staticmethod
    def domain_from_email(email: str) -> str:
        """Extract the domain portion of an email address."""
        return email.split("@")[-1].strip().lower() if "@" in email else email.strip().lower()
