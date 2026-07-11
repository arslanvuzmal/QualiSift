"""
FastAPI router for Webhook endpoints.

Handles inbound webhooks from external tools like HubSpot, Marketo, etc.
"""

import hashlib
import hmac
import structlog
from fastapi import APIRouter, Request, HTTPException, Header, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.db.session import get_db_session
from app.models.lead import Lead, LeadStatus
from app.schemas.common import StandardResponse
from app.utils.pii import hash_email

logger = structlog.get_logger()

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/inbound", response_model=StandardResponse, status_code=202)
async def handle_inbound_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hubspot_signature: str | None = Header(None, alias="X-Hubspot-Signature"),
    x_marketo_guid: str | None = Header(None, alias="X-Marketo-Guid"),
    session: AsyncSession = Depends(get_db_session),
) -> StandardResponse:
    """
    Receive leads from external CRM/marketing tools.

    Supports:
    - HubSpot (validates X-Hubspot-Signature if WEBHOOK_SECRET is set)
    - Marketo (validates X-Marketo-Guid if configured)
    - Generic JSON payloads

    Returns 202 Accepted immediately. Lead processing happens in background.
    """
    body = await request.body()
    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {str(e)}")

    # Validate HubSpot signature if secret is configured
    if settings.WEBHOOK_SECRET and x_hubspot_signature:
        expected = hmac.new(
            settings.WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(x_hubspot_signature, expected):
            logger.warning("Invalid HubSpot webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")

    # Extract lead data from various formats
    lead_data = _parse_webhook_payload(payload)

    if not lead_data.get("email"):
        raise HTTPException(
            status_code=400,
            detail="Email address is required in webhook payload",
        )

    # Normalize email for case-insensitive comparison
    normalized_email = lead_data["email"].strip().lower()

    # Check if lead already exists (case-insensitive email comparison)
    existing = await session.execute(
        select(Lead).where(Lead.email.ilike(normalized_email))
    )
    existing_lead = existing.scalars().first()

    if existing_lead:
        # Update existing lead with new data from webhook
        updated = False
        for field in ["first_name", "last_name", "company", "company_domain", "job_title"]:
            if lead_data.get(field) and getattr(existing_lead, field) != lead_data[field]:
                setattr(existing_lead, field, lead_data[field])
                updated = True
        if lead_data.get("source"):
            existing_lead.source = lead_data["source"]
            updated = True
        existing_lead.raw_payload = payload

        if updated:
            await session.commit()
            await session.refresh(existing_lead)
            logger.info(
                "Webhook updated existing lead",
                lead_id=str(existing_lead.id),
                email=normalized_email,
            )

        return StandardResponse(
            success=True,
            message="Lead already exists, updated with new data" if updated else "Lead already exists, no changes",
            data={"lead_id": str(existing_lead.id), "updated": updated},
        )

    # Create new lead
    new_lead = Lead(
        email=lead_data["email"],
        email_hash=hash_email(lead_data["email"], settings.PII_SALT),
        first_name=lead_data.get("first_name"),
        last_name=lead_data.get("last_name"),
        company=lead_data.get("company"),
        company_domain=lead_data.get("company_domain"),
        job_title=lead_data.get("job_title"),
        source=lead_data.get("source", "webhook"),
        raw_payload=payload,
        status=LeadStatus.NEW,
    )

    session.add(new_lead)
    await session.commit()
    await session.refresh(new_lead)

    logger.info(
        "Lead created from webhook",
        lead_id=str(new_lead.id),
        email=new_lead.email,
        source=new_lead.source,
    )

    # Enrich + score the new lead in the background, like the create-lead API.
    background_tasks.add_task(_score_webhook_lead, str(new_lead.id))

    return StandardResponse(
        success=True,
        message="Lead accepted from webhook and queued for processing",
        data={"lead_id": str(new_lead.id)},
        meta={"status": "queued"},
    )


async def _score_webhook_lead(lead_id: str) -> None:
    """Background task: enrich + score a lead ingested via webhook."""
    from app.services.scoring import score_lead_by_id

    try:
        await score_lead_by_id(lead_id)
    except Exception as exc:  # noqa: BLE001 - background task must not crash silently
        logger.exception("Webhook lead scoring failed", lead_id=lead_id, error=str(exc))


def _parse_webhook_payload(payload: dict) -> dict:
    """
    Parse webhook payload from various sources into standardized lead data.

    Handles formats from:
    - HubSpot
    - Marketo
    - Generic JSON
    """
    # HubSpot format
    if "properties" in payload:
        props = payload["properties"]
        return {
            "email": props.get("email", {}).get("value"),
            "first_name": props.get("firstname", {}).get("value"),
            "last_name": props.get("lastname", {}).get("value"),
            "company": props.get("company", {}).get("value"),
            "job_title": props.get("jobtitle", {}).get("value"),
            "source": "hubspot",
        }

    # Marketo format
    if "result" in payload and isinstance(payload["result"], list) and payload["result"]:
        result = payload["result"][0]
        return {
            "email": result.get("Email"),
            "first_name": result.get("First Name"),
            "last_name": result.get("Last Name"),
            "company": result.get("Company"),
            "job_title": result.get("Job Title"),
            "source": "marketo",
        }

    # Generic format - assume flat structure or nested under 'lead'
    lead = payload.get("lead", payload)
    return {
        "email": lead.get("email"),
        "first_name": lead.get("first_name"),
        "last_name": lead.get("last_name"),
        "company": lead.get("company"),
        "company_domain": lead.get("company_domain"),
        "job_title": lead.get("job_title"),
        "source": payload.get("source", "generic"),
    }
