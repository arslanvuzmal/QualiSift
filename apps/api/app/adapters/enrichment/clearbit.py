"""
Clearbit enrichment adapter.

Calls Clearbit's Company/Enrichment API over HTTP with automatic retries and
maps the response onto our normalized ``EnrichedCompanyData`` contract. Falls
back gracefully (empty data) if the company is not found.
"""

from __future__ import annotations

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.adapters.enrichment.base import EnrichedCompanyData, EnrichmentAdapter

logger = structlog.get_logger(__name__)

_COMPANY_URL = "https://company.clearbit.com/v2/companies/find"


class ClearbitEnrichmentAdapter(EnrichmentAdapter):
    """Enrichment backed by the Clearbit API."""

    name = "clearbit"

    def __init__(self, api_key: str, timeout: float = 10.0) -> None:
        if not api_key:
            raise ValueError("Clearbit API key is required for ClearbitEnrichmentAdapter")
        self._api_key = api_key
        self._timeout = timeout

    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
        reraise=True,
    )
    async def _get(self, domain: str) -> dict:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                _COMPANY_URL,
                params={"domain": domain},
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            if response.status_code == 404:
                return {}
            response.raise_for_status()
            return response.json()

    def _map(self, domain: str, payload: dict) -> EnrichedCompanyData:
        if not payload:
            return EnrichedCompanyData(company_name=domain.split(".")[0].title())
        metrics = payload.get("metrics", {}) or {}
        geo = payload.get("geo", {}) or {}
        category = payload.get("category", {}) or {}
        return EnrichedCompanyData(
            company_name=payload.get("name"),
            industry=category.get("industry"),
            employee_count=metrics.get("employees"),
            annual_revenue=metrics.get("estimatedAnnualRevenue"),
            tech_stack=payload.get("tech", []) or [],
            headquarters=", ".join(filter(None, [geo.get("city"), geo.get("state")])) or None,
            linkedin_url=(payload.get("linkedin", {}) or {}).get("handle"),
            founded_year=payload.get("foundedYear"),
        )

    async def enrich_by_domain(self, domain: str) -> EnrichedCompanyData:
        domain = domain.strip().lower()
        try:
            payload = await self._get(domain)
        except httpx.HTTPError as exc:  # pragma: no cover - network dependent
            logger.warning("Clearbit enrichment failed", domain=domain, error=str(exc))
            payload = {}
        return self._map(domain, payload)

    async def enrich_by_email(self, email: str) -> EnrichedCompanyData:
        return await self.enrich_by_domain(self.domain_from_email(email))
