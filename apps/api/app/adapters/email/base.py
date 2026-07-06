"""Email adapter base class."""

from abc import ABC, abstractmethod
from app.schemas.digest import DigestPayload


class EmailAdapter(ABC):
    """Abstract base class for email delivery adapters."""
    
    @abstractmethod
    async def send_digest(self, payload: DigestPayload, recipients: list[str]) -> bool:
        """
        Send the daily digest email to recipients.
        
        Args:
            payload: The digest payload containing lead data.
            recipients: List of email addresses to send to.
            
        Returns:
            True if sent successfully, False otherwise.
        """
        pass
