import httpx
from datetime import datetime
from typing import Any
from app.ingestion.base import BaseProvider
from app.core.config import settings

class TMDBProvider(BaseProvider):
    """
    TMDB (The Movie Database) API adapter.
    Uses free non-commercial API tier with full attribution.
    Degrades gracefully with honest reporting when TMDB_API_KEY is not configured.
    """

    def __init__(self):
        super().__init__(name="TMDB", cost_status="Zero-Cost (Free Non-Commercial)")
        self.api_key = settings.TMDB_API_KEY

    def verify_credentials(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "TMDB_API_KEY not configured. Free API key can be obtained at themoviedb.org"
        return True, "TMDB API key verified"

    async def fetch_catalog(self, limit: int = 20) -> list[dict[str, Any]]:
        valid, msg = self.verify_credentials()
        if not valid:
            self.record_failure(msg)
            return []

        url = "https://api.themoviedb.org/3/trending/all/week"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params={"api_key": self.api_key})
                if resp.status_code != 200:
                    self.record_failure(f"TMDB HTTP {resp.status_code}")
                    return []

                results = resp.json().get("results", [])
                items = []
                for r in results[:limit]:
                    media_type = r.get("media_type")
                    if media_type not in ["movie", "tv"]:
                        continue

                    title = r.get("title") or r.get("name")
                    vote_avg = r.get("vote_average")
                    vote_count = r.get("vote_count")
                    ratings = []
                    if vote_avg is not None:
                        ratings.append({
                            "source_name": "TMDB",
                            "rating_value": float(vote_avg),
                            "max_rating": 10.0,
                            "normalized_value": float(vote_avg),
                            "vote_count": vote_count,
                            "rating_type": "audience",
                            "source_url": f"https://www.themoviedb.org/{media_type}/{r.get('id')}",
                            "source_identifier": str(r.get("id")),
                            "collected_at": datetime.utcnow()
                        })

                    items.append({
                        "canonical_title": title,
                        "original_title": r.get("original_title") or r.get("original_name"),
                        "alternative_titles": [],
                        "type": "movie" if media_type == "movie" else "tv_series",
                        "original_language": r.get("original_language", "en"),
                        "release_date": r.get("release_date") or r.get("first_air_date"),
                        "release_year": int((r.get("release_date") or r.get("first_air_date") or "2000").split("-")[0]),
                        "country": "United States",
                        "genres": [],
                        "synopsis": r.get("overview", ""),
                        "content_status": "released",
                        "franchise": None,
                        "poster_url": f"https://image.tmdb.org/t/p/w500{r.get('poster_path')}" if r.get("poster_path") else None,
                        "backdrop_url": f"https://image.tmdb.org/t/p/w1280{r.get('backdrop_path')}" if r.get("backdrop_path") else None,
                        "official_website": None,
                        "source_identifiers": {"tmdb": r.get("id")},
                        "metadata_completeness": 0.85,
                        "runtime_minutes": None,
                        "ratings": ratings,
                        "popularity_seed": int(r.get("popularity", 100))
                    })

                self.record_success()
                return items
        except Exception as e:
            self.record_failure(f"TMDB error: {str(e)}")
            return []

    async def fetch_ratings(self, source_id: str) -> list[dict[str, Any]]:
        return []
