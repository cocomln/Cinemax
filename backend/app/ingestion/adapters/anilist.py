import httpx
from datetime import datetime
from typing import Any
from app.ingestion.base import BaseProvider

ANILIST_GRAPHQL_URL = "https://graphql.anilist.co"

ANILIST_CATALOG_QUERY = """
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(type: ANIME, sort: POPULARITY_DESC, startDate_greater: 19950101) {
      id
      title {
        romaji
        english
        native
      }
      synonyms
      format
      status
      episodes
      duration
      genres
      description(asHtml: false)
      startDate {
        year
        month
        day
      }
      averageScore
      popularity
      favourites
      coverImage {
        large
      }
      bannerImage
      siteUrl
    }
  }
}
"""

class AniListProvider(BaseProvider):
    """
    Real AniList GraphQL API client.
    Free, legal, open public anime metadata and audience ratings.
    """

    def __init__(self):
        super().__init__(name="AniList", cost_status="Zero-Cost (Free)")

    def verify_credentials(self) -> tuple[bool, str]:
        # Public GraphQL endpoint requires no credentials
        return True, "No credentials required (Open Public GraphQL API)"

    async def fetch_catalog(self, limit: int = 50) -> list[dict[str, Any]]:
        page_size = min(limit, 50)
        variables = {"page": 1, "perPage": page_size}
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Cinemax/1.0 (Zero-Cost Educational Entertainment Platform)"
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    ANILIST_GRAPHQL_URL,
                    json={"query": ANILIST_CATALOG_QUERY, "variables": variables},
                    headers=headers
                )
                if resp.status_code != 200:
                    self.record_failure(f"AniList API error HTTP {resp.status_code}")
                    return []
                
                data = resp.json().get("data", {}).get("Page", {}).get("media", [])
                titles = []
                for item in data:
                    fmt = (item.get("format") or "").upper()
                    if fmt == "MOVIE":
                        t_type = "anime_film"
                    elif fmt == "OVA":
                        t_type = "ova"
                    elif fmt == "ONA":
                        t_type = "ona"
                    elif fmt == "SPECIAL":
                        t_type = "special"
                    else:
                        t_type = "anime_series"

                    status_map = {
                        "FINISHED": "completed",
                        "RELEASING": "ongoing",
                        "NOT_YET_RELEASED": "upcoming",
                        "CANCELLED": "canceled"
                    }
                    content_status = status_map.get(item.get("status"), "released")

                    start_date = item.get("startDate") or {}
                    y = start_date.get("year")
                    m = start_date.get("month")
                    d = start_date.get("day")
                    release_date_str = f"{y:04d}-{m:02d}-{d:02d}" if y and m and d else (f"{y:04d}" if y else None)

                    canonical = (
                        item.get("title", {}).get("english") or 
                        item.get("title", {}).get("romaji") or 
                        "Untitled Anime"
                    )
                    original = item.get("title", {}).get("native") or item.get("title", {}).get("romaji")
                    synonyms = item.get("synonyms") or []

                    episodes_raw = item.get("episodes")
                    has_unknown_episodes = episodes_raw is None

                    avg_score = item.get("averageScore")
                    ratings = []
                    if avg_score is not None:
                        ratings.append({
                            "source_name": "AniList",
                            "rating_value": float(avg_score),
                            "max_rating": 100.0,
                            "normalized_value": round(float(avg_score) / 10.0, 2),
                            "vote_count": item.get("favourites") or item.get("popularity"),
                            "rating_type": "audience",
                            "source_url": item.get("siteUrl"),
                            "source_identifier": str(item.get("id")),
                            "collected_at": datetime.utcnow()
                        })

                    # Clean description tags
                    desc = item.get("description") or ""
                    clean_desc = desc.replace("<br>", "\n").replace("<i>", "").replace("</i>", "")

                    parsed = {
                        "canonical_title": canonical,
                        "original_title": original,
                        "alternative_titles": synonyms,
                        "type": t_type,
                        "original_language": "ja",
                        "release_date": release_date_str,
                        "release_year": y,
                        "country": "Japan",
                        "genres": item.get("genres") or [],
                        "synopsis": clean_desc,
                        "content_status": content_status,
                        "franchise": None,
                        "poster_url": (item.get("coverImage") or {}).get("large"),
                        "backdrop_url": item.get("bannerImage"),
                        "official_website": item.get("siteUrl"),
                        "source_identifiers": {"anilist": item.get("id")},
                        "metadata_completeness": 0.90,
                        "runtime_minutes": item.get("duration"),
                        "announced_episodes": episodes_raw if content_status == "upcoming" else None,
                        "released_episodes": episodes_raw if content_status in ["completed", "released"] else None,
                        "known_total_episodes": episodes_raw if not has_unknown_episodes else None,
                        "estimated_total_episodes": None,
                        "unknown_total_episodes": has_unknown_episodes,
                        "ratings": ratings,
                        "popularity_seed": item.get("popularity", 100)
                    }
                    titles.append(parsed)

                self.record_success()
                return titles
        except Exception as e:
            self.record_failure(f"AniList exception: {str(e)}")
            return []

    async def fetch_ratings(self, source_id: str) -> list[dict[str, Any]]:
        # AniList ratings are fetched directly with catalog items
        return []
