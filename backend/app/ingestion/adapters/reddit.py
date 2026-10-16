import httpx
from datetime import datetime
from typing import Any
from app.ingestion.base import BaseProvider
from app.core.config import settings
from app.scoring.sentiment import analyzer

class RedditProvider(BaseProvider):
    """
    Reddit Discussions data adapter.
    Queries public subreddit search endpoints for entertainment titles under Reddit terms.
    Gracefully degrades if credentials are not configured or rate limits are encountered.
    """

    def __init__(self):
        super().__init__(name="Reddit Discussions", cost_status="Zero-Cost (Free Tier)")

    def verify_credentials(self) -> tuple[bool, str]:
        if settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET:
            return True, "Reddit OAuth credentials configured"
        return True, "Operating in public feed search mode with standard User-Agent etiquette"

    async def fetch_discussions(self, title_query: str, subreddit: str = "movies", limit: int = 25) -> dict[str, Any]:
        """
        Search relevant public subreddit discussions for a specific title.
        """
        headers = {
            "User-Agent": settings.REDDIT_USER_AGENT
        }
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
            "q": title_query,
            "restrict_sr": "1",
            "sort": "relevance",
            "t": "week",
            "limit": limit
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=params, headers=headers)
                if resp.status_code == 429:
                    self.record_failure("Reddit API rate limit (HTTP 429). Exponential backoff requested.")
                    return {"post_count": 0, "engagement": 0, "sentiment": {"positive": 0, "neutral": 1, "negative": 0}}
                if resp.status_code != 200:
                    self.record_failure(f"Reddit HTTP {resp.status_code}")
                    return {"post_count": 0, "engagement": 0, "sentiment": {"positive": 0, "neutral": 1, "negative": 0}}

                data = resp.json().get("data", {}).get("children", [])
                post_count = len(data)
                total_engagement = 0
                sentiments = []

                for child in data:
                    item = child.get("data", {})
                    score = item.get("score", 0)
                    num_comments = item.get("num_comments", 0)
                    total_engagement += (score + num_comments)
                    
                    title_text = item.get("title", "")
                    sentiments.append(analyzer.analyze_text(title_text))

                pos_avg = sum(s["positive"] for s in sentiments) / max(1, len(sentiments))
                neg_avg = sum(s["negative"] for s in sentiments) / max(1, len(sentiments))
                neu_avg = sum(s["neutral"] for s in sentiments) / max(1, len(sentiments))

                self.record_success()
                return {
                    "post_count": post_count,
                    "engagement": total_engagement,
                    "sentiment": {
                        "positive": round(pos_avg, 3),
                        "neutral": round(neu_avg, 3),
                        "negative": round(neg_avg, 3)
                    }
                }
        except Exception as e:
            self.record_failure(f"Reddit search error: {str(e)}")
            return {
                "post_count": 0,
                "engagement": 0,
                "sentiment": {"positive": 0.0, "neutral": 1.0, "negative": 0.0}
            }

    async def fetch_catalog(self, limit: int = 50) -> list[dict[str, Any]]:
        return []

    async def fetch_ratings(self, source_id: str) -> list[dict[str, Any]]:
        return []
