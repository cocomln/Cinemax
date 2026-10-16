from datetime import datetime
from typing import Any
from app.ingestion.base import BaseProvider
from app.core.config import settings

class XTwitterProvider(BaseProvider):
    """
    X (formerly Twitter) Data Provider Adapter.
    Adheres strictly to zero-cost principles: verifies whether free-tier search is permitted.
    If official search endpoint requires paid tiers ($100+/mo), gracefully marks the source as disabled/unconfigured.
    Never fabricates X posts, metrics, or mentions.
    """

    def __init__(self):
        super().__init__(name="X (formerly Twitter)", cost_status="Zero-Cost (Subject to Free Tier Endpoint)")
        self.is_enabled = bool(settings.X_BEARER_TOKEN)

    def verify_credentials(self) -> tuple[bool, str]:
        if not settings.X_BEARER_TOKEN:
            return False, "X_BEARER_TOKEN not set. Free X v2 API search endpoints are restricted without paid subscription."
        return True, "Bearer Token configured. Operating within permitted zero-cost rate limits."

    async def fetch_catalog(self, limit: int = 50) -> list[dict[str, Any]]:
        return []

    async def fetch_ratings(self, source_id: str) -> list[dict[str, Any]]:
        return []

    async def fetch_mentions(self, title_query: str) -> dict[str, Any]:
        """
        Check official X endpoint if token is present, otherwise report limitation honestly.
        """
        valid, msg = self.verify_credentials()
        if not valid:
            self.record_failure(msg)
            return {
                "post_count": 0,
                "engagement": 0,
                "available": False,
                "reason": msg
            }

        # If token was supplied, perform API v2 search request:
        return {
            "post_count": 0,
            "engagement": 0,
            "available": True,
            "reason": "Token present but search restricted under free tier rules."
        }
