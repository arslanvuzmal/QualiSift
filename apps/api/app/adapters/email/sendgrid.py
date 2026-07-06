"""SendGrid email adapter for production use."""

import structlog
import httpx
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from typing import Optional

from app.adapters.email.base import EmailAdapter
from app.schemas.digest import DigestPayload

logger = structlog.get_logger()


class SendGridEmailAdapter(EmailAdapter):
    """Email adapter using SendGrid API for sending digest emails."""
    
    def __init__(
        self,
        api_key: str,
        from_email: str,
        template_dir: str | None = None
    ):
        self.api_key = api_key
        self.from_email = from_email
        self.api_url = "https://api.sendgrid.com/v3/mail/send"
        
        if template_dir is None:
            template_dir = Path(__file__).parent.parent.parent / "templates"
        
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
    
    async def send_digest(self, payload: DigestPayload, recipients: list[str]) -> bool:
        """
        Send the digest email via SendGrid API.
        
        Args:
            payload: The digest payload.
            recipients: List of recipient email addresses.
            
        Returns:
            True if sent successfully, False otherwise.
        """
        try:
            template = self.env.get_template("digest_email.html")
            
            html_content = template.render(
                run_date=payload.run_date,
                total_leads=payload.total_leads,
                hot_count=payload.hot_count,
                warm_count=payload.warm_count,
                cold_count=payload.cold_count,
                hot_leads=payload.hot_leads,
                warm_leads=payload.warm_leads
            )
            
            # Build SendGrid payload
            personalizations = [
                {
                    "to": [{"email": recipient} for recipient in recipients],
                    "subject": f"🎯 Daily Lead Digest - {payload.run_date.strftime('%B %d, %Y')}"
                }
            ]
            
            payload_data = {
                "personalizations": personalizations,
                "from": {"email": self.from_email, "name": "AI Sales Lead Qualifier"},
                "content": [
                    {
                        "type": "text/html",
                        "value": html_content
                    }
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload_data,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 202:
                    logger.info(
                        "Digest email sent successfully via SendGrid",
                        recipients=recipients
                    )
                    return True
                else:
                    logger.error(
                        "SendGrid API returned error",
                        status_code=response.status_code,
                        body=response.text
                    )
                    return False
            
        except Exception as e:
            logger.error("Failed to send digest email via SendGrid", error=str(e))
            return False
