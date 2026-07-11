"""
FastAPI routers for the AI Sales Lead Qualifier API.

This package contains all API route handlers organized by resource.
"""

from app.routers import leads, scoring, digest, criteria, webhooks, health

__all__ = [
    "leads",
    "scoring",
    "digest",
    "criteria",
    "webhooks",
    "health",
]
