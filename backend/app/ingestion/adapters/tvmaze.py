import httpx
from datetime import datetime
from typing import Any
from app.ingestion.base import BaseProvider

TVMAZE_BASE_URL = "https://api.tvmaze.com"

# Sample set of high-impact television series from 1995 to present across drama, sci-fi, comedy, and upcoming
TV_CURATED_SEEDS = [
    "Breaking Bad", "Game of Thrones", "Stranger Things", "Succession",
    "The Last of Us", "Severance", "Shogun", "Fallout", "House of the Dragon",
    "Chernobyl", "Better Call Saul", "The Bear", "Fargo", "The Boys",
    "Westworld", "True Detective", "The Sopranos", "The Wire", "Andor",
    "Dune: Prophecy"
]

class TVmazeProvider(BaseProvider):
    """
    Real TVmaze REST API client for television metadata, seasons, and episodes.
    Licensed under Creative Commons BY-SA 4.0 via TVmaze API. No API key needed.
    """

    def __init__(self):
        super().__init__(name="TVmaze", cost_status="Zero-Cost (Free)")

    def verify_credentials(self) -> tuple[bool, str]:
        return True, "No credentials required (Open Public REST API)"

    async def fetch_catalog(self, limit: int = 20) -> list[dict[str, Any]]:
        titles = []
        headers = {
            "User-Agent": "Cinemax/1.0 (Zero-Cost Educational Platform)"
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                for show_name in TV_CURATED_SEEDS[:limit]:
                    try:
                        resp = await client.get(
                            f"{TVMAZE_BASE_URL}/singlesearch/shows",
                            params={"q": show_name, "embed": "episodes"},
                            headers=headers
                        )
                        if resp.status_code != 200:
                            continue

                        show = resp.json()
                        premiered = show.get("premiered") # "YYYY-MM-DD"
                        release_year = int(premiered.split("-")[0]) if premiered else None
                        
                        # Filter to 1995 or newer as per specification
                        if release_year and release_year < 1995:
                            continue

                        status_raw = (show.get("status") or "").lower()
                        if status_raw == "ended":
                            content_status = "completed"
                        elif status_raw == "running":
                            content_status = "ongoing"
                        elif status_raw in ["to be determined", "in development"]:
                            content_status = "upcoming"
                        else:
                            content_status = "released"

                        # Parse embedded episodes
                        embedded_episodes = show.get("_embedded", {}).get("episodes") or []
                        parsed_episodes = []
                        released_count = 0
                        for ep in embedded_episodes:
                            parsed_episodes.append({
                                "season_number": ep.get("season"),
                                "episode_number": ep.get("number") or 1,
                                "episode_title": ep.get("name"),
                                "release_date": ep.get("airdate"),
                                "runtime_minutes": ep.get("runtime"),
                                "is_special": ep.get("type") != "regular",
                                "source": "TVmaze",
                                "source_identifier": str(ep.get("id"))
                            })
                            if ep.get("airdate") and ep.get("airdate") <= datetime.utcnow().strftime("%Y-%m-%d"):
                                released_count += 1

                        total_eps = len(embedded_episodes) if embedded_episodes else None
                        is_unknown_eps = total_eps is None or (content_status == "ongoing" and total_eps == 0)

                        # Ratings
                        rating_val = (show.get("rating") or {}).get("average")
                        ratings = []
                        if rating_val is not None:
                            ratings.append({
                                "source_name": "TVmaze",
                                "rating_value": float(rating_val),
                                "max_rating": 10.0,
                                "normalized_value": float(rating_val),
                                "vote_count": None,
                                "rating_type": "audience",
                                "source_url": show.get("url"),
                                "source_identifier": str(show.get("id")),
                                "collected_at": datetime.utcnow()
                            })

                        # Summary cleanup
                        summary_raw = show.get("summary") or ""
                        clean_summary = summary_raw.replace("<p>", "").replace("</p>", "").replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")

                        network = (show.get("network") or {}).get("name") or (show.get("webChannel") or {}).get("name")
                        image = show.get("image") or {}

                        titles.append({
                            "canonical_title": show.get("name"),
                            "original_title": show.get("name"),
                            "alternative_titles": [],
                            "type": "tv_series",
                            "original_language": (show.get("language") or "English").lower()[:2],
                            "release_date": premiered,
                            "release_year": release_year,
                            "country": ((show.get("network") or {}).get("country") or {}).get("name") or "United States",
                            "genres": show.get("genres") or [],
                            "synopsis": clean_summary,
                            "content_status": content_status,
                            "franchise": network,
                            "poster_url": image.get("original") or image.get("medium"),
                            "backdrop_url": None,
                            "official_website": show.get("officialSite") or show.get("url"),
                            "source_identifiers": {"tvmaze": show.get("id")},
                            "metadata_completeness": 0.88,
                            "runtime_minutes": show.get("averageRuntime") or show.get("runtime"),
                            "announced_episodes": total_eps if content_status == "upcoming" else None,
                            "released_episodes": released_count if released_count > 0 else total_eps,
                            "known_total_episodes": total_eps if content_status == "completed" else None,
                            "estimated_total_episodes": total_eps if content_status == "ongoing" else None,
                            "unknown_total_episodes": is_unknown_eps,
                            "ratings": ratings,
                            "episodes": parsed_episodes,
                            "popularity_seed": int((rating_val or 7.0) * 150)
                        })
                    except Exception as show_err:
                        continue

                self.record_success()
                return titles
        except Exception as e:
            self.record_failure(f"TVmaze error: {str(e)}")
            return []

    async def fetch_ratings(self, source_id: str) -> list[dict[str, Any]]:
        return []
