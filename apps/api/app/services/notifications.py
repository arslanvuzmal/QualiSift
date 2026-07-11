"""Notification service factory and integration."""

import structlog
import os
from typing import Optional

from app.adapters.email.base import EmailAdapter
from app.adapters.email.console import ConsoleEmailAdapter
from app.adapters.email.smtp import SMTPEmailAdapter
from app.adapters.email.sendgrid import SendGridEmailAdapter
from app.adapters.notifications.slack import SlackAdapter
from app.services.digest import DigestService

logger = structlog.get_logger()


def get_email_adapter() -> EmailAdapter:
    """
    Factory function to get the appropriate email adapter based on environment.
    
    Returns:
        Configured EmailAdapter instance.
    """
    provider = os.getenv("EMAIL_PROVIDER", "console").lower()
    
    if provider == "console":
        logger.info("Using console email adapter")
        return ConsoleEmailAdapter()
    
    elif provider == "smtp":
        logger.info("Using SMTP email adapter")
        return SMTPEmailAdapter(
            smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("SMTP_USERNAME", ""),
            password=os.getenv("SMTP_PASSWORD", ""),
            from_email=os.getenv("FROM_EMAIL", "")
        )
    
    elif provider == "sendgrid":
        logger.info("Using SendGrid email adapter")
        return SendGridEmailAdapter(
            api_key=os.getenv("SENDGRID_API_KEY", ""),
            from_email=os.getenv("FROM_EMAIL", "")
        )
    
    else:
        logger.warning(f"Unknown email provider '{provider}', falling back to console")
        return ConsoleEmailAdapter()


def get_slack_adapter() -> Optional[SlackAdapter]:
    """
    Factory function to get the Slack adapter if configured.
    
    Returns:
        SlackAdapter instance or None if not configured.
    """
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if webhook_url:
        logger.info("Slack notifications enabled")
        return SlackAdapter(webhook_url=webhook_url)
    else:
        logger.info("Slack notifications disabled (no webhook URL)")
        return None


class NotificationService:
    """Service for orchestrating digest notifications."""
    
    def __init__(self, digest_service: DigestService):
        self.digest_service = digest_service
        self.email_adapter = get_email_adapter()
        self.slack_adapter = get_slack_adapter()
    
    async def send_daily_digest(self, recipients: list[str]) -> bool:
        """
        Compile and send the daily digest via all configured channels.
        
        Args:
            recipients: List of email addresses for the digest.
            
        Returns:
            True if all notifications sent successfully, False otherwise.
        """
        try:
            # Compile the digest
            payload = await self.digest_service.compile_digest()
            
            email_success = False
            slack_success = False
            
            # Send email
            email_success = await self.email_adapter.send_digest(payload, recipients)
            
            # Send Slack notification
            if self.slack_adapter:
                slack_success = await self.slack_adapter.send_digest(payload)
            else:
                slack_success = True  # Consider success if Slack not configured
            
            success = email_success and slack_success
            
            if success:
                logger.info(
                    "Daily digest sent successfully",
                    email_sent=email_success,
                    slack_sent=slack_success
                )
            else:
                logger.warning(
                    "Daily digest partially failed",
                    email_sent=email_success,
                    slack_sent=slack_success
                )
            
            return success
            
        except Exception as e:
            logger.error("Failed to send daily digest", error=str(e))
            return False
