"""SMTP email adapter for production use."""

import structlog
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from app.adapters.email.base import EmailAdapter
from app.schemas.digest import DigestPayload

logger = structlog.get_logger()


class SMTPEmailAdapter(EmailAdapter):
    """Email adapter using SMTP for sending digest emails."""
    
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
        template_dir: str | None = None,
        use_tls: bool = True
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.use_tls = use_tls
        
        if template_dir is None:
            template_dir = Path(__file__).parent.parent.parent / "templates"
        
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
    
    async def send_digest(self, payload: DigestPayload, recipients: list[str]) -> bool:
        """
        Send the digest email via SMTP.
        
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
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"🎯 Daily Lead Digest - {payload.run_date.strftime('%B %d, %Y')}"
            message["From"] = self.from_email
            message["To"] = ", ".join(recipients)
            
            # Attach HTML content
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)
            
            # Send via SMTP
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.username,
                password=self.password,
                start_tls=self.use_tls
            )
            
            logger.info(
                "Digest email sent successfully via SMTP",
                recipients=recipients,
                host=self.smtp_host
            )
            
            return True
            
        except Exception as e:
            logger.error("Failed to send digest email via SMTP", error=str(e))
            return False
