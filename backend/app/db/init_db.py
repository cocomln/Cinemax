import json
from datetime import datetime
from app.db.session import engine, Base, SessionLocal
from app.db.models import SourceRegistryEntry

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Pre-seed source registry if not already present
        seed_providers = [
            {
                "provider_name": "AniList",
                "provider_type": "catalog & ratings",
                "supported_fields_json": json.dumps(["canonical_title", "original_title", "episodes", "status", "genres", "ratings", "poster_url", "release_date"]),
                "access_method": "GraphQL API",
                "auth_requirement": "None (Free Public API)",
                "cost_status": "Zero-Cost (Free)",
                "license_url": "https://anilist.co/terms",
                "attribution_text": "Data provided by AniList.co under free public API terms.",
                "rate_limit_info": "90 requests per minute",
                "data_retention_rules": "Cached title metadata and ratings refreshed periodically.",
                "is_enabled": True,
                "coverage_limitations": "Comprehensive anime catalog (films, series, OVAs, ONAs, specials)."
            },
            {
                "provider_name": "TVmaze",
                "provider_type": "catalog & episodes",
                "supported_fields_json": json.dumps(["canonical_title", "seasons", "episodes", "air_dates", "runtime", "genres", "synopsis", "poster_url"]),
                "access_method": "REST API",
                "auth_requirement": "None (Free Public API)",
                "cost_status": "Zero-Cost (Free)",
                "license_url": "https://www.tvmaze.com/api",
                "attribution_text": "Television metadata licensed under Creative Commons BY-SA 4.0 via TVmaze API.",
                "rate_limit_info": "20 requests per 10 seconds",
                "data_retention_rules": "Periodic scheduled catalog refresh.",
                "is_enabled": True,
                "coverage_limitations": "Global television coverage from 1995 to present and announced releases."
            },
            {
                "provider_name": "Wikidata",
                "provider_type": "catalog & cross-references",
                "supported_fields_json": json.dumps(["canonical_title", "original_title", "release_year", "imdb_id", "country", "director", "genres"]),
                "access_method": "SPARQL Endpoint",
                "auth_requirement": "None (Free Open Endpoint)",
                "cost_status": "Zero-Cost (Free)",
                "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "attribution_text": "Structured movie and television facts from Wikidata under CC0 1.0 Universal Public Domain.",
                "rate_limit_info": "Fair-use with User-Agent header",
                "data_retention_rules": "Persisted entity IDs and release attributes.",
                "is_enabled": True,
                "coverage_limitations": "Extensive multilingual cinema and TV entity identifiers."
            },
            {
                "provider_name": "Kaggle Dataset Importer",
                "provider_type": "historical files & catalog",
                "supported_fields_json": json.dumps(["movie_metadata", "tv_metadata", "historical_ratings", "vote_counts", "runtime", "box_office"]),
                "access_method": "Local CSV / JSON / Parquet Import & CLI",
                "auth_requirement": "Free Kaggle credentials for CLI; none for local files",
                "cost_status": "Zero-Cost (Free)",
                "license_url": "https://www.kaggle.com/terms",
                "attribution_text": "Imported datasets attributed to respective Kaggle publishers and open licenses.",
                "rate_limit_info": "Incremental offline processing without automated bulk spamming",
                "data_retention_rules": "Normalized storage in Cinemax SQLite/PostgreSQL schema.",
                "is_enabled": True,
                "coverage_limitations": "Historical data points from verified open datasets."
            },
            {
                "provider_name": "Reddit Discussions",
                "provider_type": "social activity",
                "supported_fields_json": json.dumps(["post_counts", "comment_counts", "discussion_velocity", "engagement"]),
                "access_method": "Official API / Public JSON feeds",
                "auth_requirement": "Free Developer App Credentials",
                "cost_status": "Zero-Cost (Free Tier)",
                "license_url": "https://www.redditinc.com/policies/data-api-terms",
                "attribution_text": "Discussions aggregated via Reddit public API under Developer Terms.",
                "rate_limit_info": "60 requests per minute with backoff",
                "data_retention_rules": "Aggregated metrics only; no private user text retained.",
                "is_enabled": True,
                "coverage_limitations": "Public entertainment subreddits (r/movies, r/television, r/anime)."
            },
            {
                "provider_name": "X (formerly Twitter)",
                "provider_type": "social activity",
                "supported_fields_json": json.dumps(["mention_counts", "engagement_velocity"]),
                "access_method": "Official API v2",
                "auth_requirement": "Bearer Token",
                "cost_status": "Zero-Cost (Verified Free Tier Availability)",
                "license_url": "https://developer.x.com/en/developer-terms",
                "attribution_text": "Public mention metrics via official X Developer API.",
                "rate_limit_info": "Per official tier specification",
                "data_retention_rules": "Aggregated velocity counts only.",
                "is_enabled": False, # Disabled by default until zero-cost credentials confirmed
                "coverage_limitations": "Subject to free access search endpoint availability without charges."
            },
            {
                "provider_name": "TMDB",
                "provider_type": "ratings & catalog",
                "supported_fields_json": json.dumps(["ratings", "vote_counts", "runtime", "poster_url", "backdrop_url"]),
                "access_method": "REST API v3",
                "auth_requirement": "Free API Key (Optional)",
                "cost_status": "Zero-Cost (Free Non-Commercial)",
                "license_url": "https://www.themoviedb.org/terms-of-use",
                "attribution_text": "This product uses the TMDB API but is not endorsed or certified by TMDB.",
                "rate_limit_info": "40 requests per 10 seconds",
                "data_retention_rules": "Cached ratings and poster references.",
                "is_enabled": True,
                "coverage_limitations": "General entertainment catalog; fallback gracefully when API key not set."
            }
        ]

        for p in seed_providers:
            existing = db.query(SourceRegistryEntry).filter_by(provider_name=p["provider_name"]).first()
            if not existing:
                db.add(SourceRegistryEntry(**p))
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Database schema and Source Registry initialized successfully.")
