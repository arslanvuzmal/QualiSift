"""
Enrichment provider factory.

Selects the enrichment adapter based on ``settings.ENRICHMENT_PROVIDER`` so the
rest of the app depends only on the ``EnrichmentAdapter`` interface. Falls back
to the mock provider when a real provider is requested without credentials.
"""

from __future__ import annotations

from functools import lru_cache

import structlog

from app.adapters.enrichment.base import EnrichmentAdapter
from app.adapters.enrichment.clearbit import ClearbitEnrichmentAdapter
from app.adapters.enrichment.mock import MockEnrichmentAdapter
from app.config import settings

logger = structlog.get_logger(__name__)


@lru_cache
def get_enrichment_adapter() -> EnrichmentAdapter:
    """Return the configured enrichment adapter (cached singleton)."""
    provider = (settings.ENRICHMENT_PROVIDER or "mock").lower()

    if provider == "clearbit":
        if settings.CLEARBIT_API_KEY:
            return ClearbitEnrichmentAdapter(api_key=settings.CLEARBIT_API_KEY)
        logger.warning("CLEARBIT_API_KEY not set - falling back to mock enrichment")
        return MockEnrichmentAdapter()

    if provider != "mock":
        logger.warning("Unknown enrichment provider - using mock", provider=provider)
    return MockEnrichmentAdapter()
