"""Console email adapter for local development/testing."""

import sys

import structlog
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from app.adapters.email.base import EmailAdapter
from app.schemas.digest import DigestPayload

logger = structlog.get_logger()


def _print(text: str) -> None:
    """Print in whatever encoding the console has. The email contains emoji, which a Windows
    console (cp1252) cannot encode; the error used to mark the whole digest as failed."""
    encoding = sys.stdout.encoding or "utf-8"
    print(text.encode(encoding, errors="replace").decode(encoding))


class ConsoleEmailAdapter(EmailAdapter):
    """Email adapter that prints HTML to console for local testing."""
    
    def __init__(self, template_dir: str | None = None):
        if template_dir is None:
            template_dir = Path(__file__).parent.parent.parent / "templates"
        
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
    
    async def send_digest(self, payload: DigestPayload, recipients: list[str]) -> bool:
        """
        Render and print the digest HTML to console.
        
        Args:
            payload: The digest payload.
            recipients: List of recipient emails (logged only).
            
        Returns:
            True always (for testing purposes).
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
            
            logger.info(
                "Digest email rendered (console mode)",
                recipients=recipients,
                total_leads=payload.total_leads,
                hot_count=payload.hot_count
            )
            
            # Print to console for verification
            _print("\n" + "="*80)
            _print("📧 DIGEST EMAIL PREVIEW (Console Mode)")
            _print("="*80)
            _print(f"To: {', '.join(recipients)}")
            _print(f"Date: {payload.run_date.strftime('%Y-%m-%d')}")
            _print(f"Stats: {payload.hot_count} Hot, {payload.warm_count} Warm, {payload.cold_count} Cold")
            _print("="*80)
            _print(html_content[:2000] + "..." if len(html_content) > 2000 else html_content)
            _print("="*80 + "\n")
            
            return True
            
        except Exception as e:
            logger.error("Failed to render digest email", error=str(e))
            return False
