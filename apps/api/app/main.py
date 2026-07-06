"""
FastAPI application entry point for the AI Sales Lead Qualifier.

This module initializes the FastAPI application with all routers,
middleware, and configuration for production use.
"""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.routers import leads, scoring, digest, criteria, webhooks, health

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    logger.info("Starting AI Sales Lead Qualifier API")
    yield
    logger.info("Shutting down AI Sales Lead Qualifier API")


# Initialize FastAPI application
app = FastAPI(
    title="AI Sales Lead Qualifier API",
    description="API for qualifying sales leads using AI enrichment and scoring",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Initialize rate limiter
rate_limiter = Limiter(key_func=get_remote_address)
app.state.limiter = rate_limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions and return standard error format."""
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else None,
        },
    )


# Include routers with rate limiting
app.include_router(
    leads.router,
    prefix="/api/v1",
    tags=["leads"],
    dependencies=[],  # Add auth dependencies here in production
)
app.include_router(
    scoring.router,
    prefix="/api/v1",
    tags=["scoring"],
)
app.include_router(
    digest.router,
    prefix="/api/v1",
    tags=["digest"],
)
app.include_router(
    criteria.router,
    prefix="/api/v1",
    tags=["criteria"],
)
app.include_router(
    webhooks.router,
    prefix="/api/v1",
    tags=["webhooks"],
    # Higher limit for webhooks as they may receive bursts
)
app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["health"],
)


# Apply rate limits to specific routes
@rate_limiter.limit("100/minute")
@app.get("/api/v1/leads")
async def list_leads_rate_limited():
    """Placeholder to apply rate limit to leads endpoint."""
    pass


@rate_limiter.limit("1000/minute")
@app.post("/api/v1/webhooks/inbound")
async def webhook_rate_limited():
    """Placeholder to apply higher rate limit to webhooks."""
    pass


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Simple health check endpoint (no DB dependency).

    Returns:
        dict: Status indicator showing the API is running.
    """
    return {"status": "ok"}


@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint with API information.

    Returns:
        dict: Basic API information.
    """
    return {
        "name": "AI Sales Lead Qualifier API",
        "version": "0.1.0",
        "docs": "/docs",
    }
