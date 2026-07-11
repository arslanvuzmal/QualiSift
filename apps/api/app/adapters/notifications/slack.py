"""Slack notification adapter using Block Kit."""

import structlog
import httpx

from app.schemas.digest import DigestPayload

logger = structlog.get_logger()


class SlackAdapter:
    """Slack adapter for sending digest notifications via Block Kit."""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def _build_block_kit_payload(self, payload: DigestPayload) -> dict:
        """
        Build a Slack Block Kit payload from the digest data.
        
        Args:
            payload: The digest payload.
            
        Returns:
            Dict containing the Block Kit JSON structure.
        """
        blocks = [
            # Header
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎯 Daily Lead Digest",
                    "emoji": True
                }
            },
            # Date section
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Date:* {payload.run_date.strftime('%B %d, %Y')}"
                }
            },
            # Divider
            {"type": "divider"},
            # Stats section
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Processed*\n{payload.total_leads}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*🔥 Hot*\n{payload.hot_count}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*🟡 Warm*\n{payload.warm_count}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*❌ Cold*\n{payload.cold_count}"
                    }
                ]
            },
            {"type": "divider"}
        ]
        
        # Add top hot leads (limit to 3 for brevity)
        if payload.hot_leads:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🔥 Top Hot Leads ({len(payload.hot_leads)} total)*"
                }
            })
            
            for lead in payload.hot_leads[:3]:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{lead.company}*\n{lead.first_name} {lead.last_name} • {lead.job_title}\n*Score:* {lead.composite_score:.0f}/100\n_{lead.overall_summary}_"
                    }
                })
                
                # Action button for each lead
                blocks.append({
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View Details",
                                "emoji": True
                            },
                            "url": "#",
                            "action_id": f"view_lead_{lead.id}"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Draft Email",
                                "emoji": True
                            },
                            "url": "#",
                            "action_id": f"draft_email_{lead.id}"
                        }
                    ]
                })
                blocks.append({"type": "divider"})
        
        # Footer with action button
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Full Dashboard",
                        "emoji": True
                    },
                    "url": "#",
                    "action_id": "view_dashboard"
                }
            ]
        })
        
        return {"blocks": blocks}
    
    async def send_digest(self, payload: DigestPayload) -> bool:
        """
        Send the digest notification to Slack.
        
        Args:
            payload: The digest payload.
            
        Returns:
            True if sent successfully, False otherwise.
        """
        try:
            block_kit_payload = self._build_block_kit_payload(payload)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=block_kit_payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info(
                        "Digest notification sent to Slack",
                        hot_count=payload.hot_count,
                        warm_count=payload.warm_count
                    )
                    return True
                else:
                    logger.error(
                        "Slack webhook returned error",
                        status_code=response.status_code,
                        body=response.text
                    )
                    return False
                    
        except Exception as e:
            logger.error("Failed to send digest notification to Slack", error=str(e))
            return False
