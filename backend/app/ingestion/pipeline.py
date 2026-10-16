import json
import logging
from datetime import datetime, timedelta
from typing import Any
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import (
    Title, Episode, Rating, SocialMetric, HistoricalObservation,
    Prediction, SourceRegistryEntry
)
from app.ingestion.registry import registry
from app.scoring.popularity import popularity_engine
from app.ml.engine import prediction_engine
from app.arena.game import arena_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cinemax_pipeline")

class IngestionPipeline:
    """
    Automated idempotent refresh pipeline for Cinemax.
    Runs daily at midnight IST (18:30 UTC), deduplicates cross-source records,
    computes multi-factor popularity scores, records time-series snapshots,
    and updates ML predictions.
    """

    def __init__(self):
        self.last_run_summary: dict[str, Any] = {
            "status": "idle",
            "last_refresh_utc": None,
            "last_refresh_ist": None,
            "titles_processed": 0,
            "sources_synced": []
        }

    async def run_pipeline(self, db: Session | None = None) -> dict[str, Any]:
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True

        synced_sources = []
        errors = []
        now_utc = datetime.utcnow()
        # IST is UTC + 5:30
        now_ist = now_utc + timedelta(hours=5, minutes=30)

        logger.info(f"Starting Cinemax Ingestion Pipeline at UTC {now_utc.isoformat()} (IST {now_ist.isoformat()})")

        total_ingested = 0

        try:
            # 1. AniList Ingestion (Anime)
            anilist_provider = registry.anilist
            try:
                anime_records = await anilist_provider.fetch_catalog(limit=40)
                for item in anime_records:
                    self._upsert_title_and_relations(db, item, provider_name="AniList")
                    total_ingested += 1
                synced_sources.append("AniList")
                self._update_registry_entry(db, "AniList", True)
            except Exception as e:
                logger.error(f"AniList ingestion failed: {e}")
                errors.append(f"AniList: {str(e)}")
                self._update_registry_entry(db, "AniList", False, str(e))

            # 2. TVmaze Ingestion (TV Series)
            tvmaze_provider = registry.tvmaze
            try:
                tv_records = await tvmaze_provider.fetch_catalog(limit=25)
                for item in tv_records:
                    self._upsert_title_and_relations(db, item, provider_name="TVmaze")
                    total_ingested += 1
                synced_sources.append("TVmaze")
                self._update_registry_entry(db, "TVmaze", True)
            except Exception as e:
                logger.error(f"TVmaze ingestion failed: {e}")
                errors.append(f"TVmaze: {str(e)}")
                self._update_registry_entry(db, "TVmaze", False, str(e))

            # 3. Wikidata Ingestion (Movies)
            wikidata_provider = registry.wikidata
            try:
                movie_records = await wikidata_provider.fetch_catalog(limit=20)
                for item in movie_records:
                    self._upsert_title_and_relations(db, item, provider_name="Wikidata")
                    total_ingested += 1
                synced_sources.append("Wikidata")
                self._update_registry_entry(db, "Wikidata", True)
            except Exception as e:
                logger.error(f"Wikidata ingestion failed: {e}")
                errors.append(f"Wikidata: {str(e)}")
                self._update_registry_entry(db, "Wikidata", False, str(e))

            # 4. Kaggle Ingestion (Local Datasets if present)
            kaggle_provider = registry.kaggle
            try:
                kaggle_records = await kaggle_provider.fetch_catalog(limit=25)
                for item in kaggle_records:
                    self._upsert_title_and_relations(db, item, provider_name="Kaggle")
                    total_ingested += 1
                if kaggle_records:
                    synced_sources.append("Kaggle Dataset Importer")
                self._update_registry_entry(db, "Kaggle Dataset Importer", True)
            except Exception as e:
                logger.warning(f"Kaggle ingestion skipped/empty: {e}")

            # 5. Compute Popularity Scores & Historical Snapshots for All Titles
            all_titles = db.query(Title).all()
            for title in all_titles:
                # Calculate active sources count
                src_ids = json.loads(title.source_identifiers_json or "{}")
                active_sources = max(1, len(src_ids))

                # Approximate recent activity from ratings and seed popularity
                base_activity = int(title.metadata_completeness * 200)
                if title.ratings:
                    total_votes = sum(r.vote_count or 100 for r in title.ratings)
                    recent_mentions = max(50, int(total_votes / 250))
                else:
                    recent_mentions = 45 if title.content_status == "upcoming" else 15

                prior_mentions = max(20, int(recent_mentions * 0.9))
                engagements = recent_mentions * 4

                pop_res = popularity_engine.calculate_popularity(
                    recent_mentions=recent_mentions,
                    prior_mentions=prior_mentions,
                    total_engagements=engagements,
                    active_sources_count=active_sources,
                    total_possible_sources=4,
                    historical_consistency_ratio=0.75
                )

                title.current_popularity_score = pop_res["total_score"]
                title.popularity_growth_velocity = pop_res["growth_velocity_score"] - 50.0 # velocity offset
                title.popularity_source_coverage = pop_res["source_coverage"]

                # Add immutable historical observation for today (idempotent for current hour)
                today_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
                existing_obs = db.query(HistoricalObservation).filter(
                    HistoricalObservation.title_id == title.id,
                    HistoricalObservation.metric_name == "popularity_score",
                    HistoricalObservation.timestamp >= today_start
                ).first()

                if not existing_obs:
                    obs = HistoricalObservation(
                        title_id=title.id,
                        metric_name="popularity_score",
                        metric_value=pop_res["total_score"],
                        observation_window="24h",
                        timestamp=now_utc,
                        source="cinemax_multi_source",
                        confidence=pop_res["source_coverage"],
                        data_quality_status="verified" if pop_res["has_sufficient_data"] else "insufficient_data"
                    )
                    db.add(obs)

                # Recompute 7-day prediction
                pred_res = prediction_engine.predict_7d(title)
                existing_pred = db.query(Prediction).filter_by(title_id=title.id).first()
                if not existing_pred:
                    pred = Prediction(
                        title_id=title.id,
                        horizon_days=7,
                        target_metric="popularity_score",
                        current_score=pop_res["total_score"],
                        predicted_score=pred_res["predicted_score"],
                        predicted_change=pred_res["predicted_change"],
                        uncertainty_lower=pred_res["uncertainty_lower"],
                        uncertainty_upper=pred_res["uncertainty_upper"],
                        model_version=pred_res["model_version"],
                        contributing_factors_json=json.dumps(pred_res["contributing_factors"])
                    )
                    db.add(pred)
                else:
                    existing_pred.current_score = pop_res["total_score"]
                    existing_pred.predicted_score = pred_res["predicted_score"]
                    existing_pred.predicted_change = pred_res["predicted_change"]
                    existing_pred.uncertainty_lower = pred_res["uncertainty_lower"]
                    existing_pred.uncertainty_upper = pred_res["uncertainty_upper"]
                    existing_pred.model_version = pred_res["model_version"]
                    existing_pred.contributing_factors_json = json.dumps(pred_res["contributing_factors"])
                    existing_pred.generated_at = now_utc

            # Resolve any due Prediction Arena guesses
            arena_service.resolve_completed_guesses(db)

            db.commit()

            status_str = "success" if not errors else ("partial_success" if synced_sources else "failed")
            self.last_run_summary = {
                "status": status_str,
                "last_refresh_utc": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "last_refresh_ist": now_ist.strftime("%Y-%m-%d %I:%M:%S %p IST"),
                "titles_processed": len(all_titles),
                "sources_synced": synced_sources,
                "errors": errors
            }
            logger.info(f"Pipeline completed: {self.last_run_summary}")
            return self.last_run_summary
        except Exception as overall_e:
            db.rollback()
            logger.error(f"Fatal error in pipeline: {overall_e}")
            self.last_run_summary = {
                "status": "failed",
                "last_refresh_utc": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "last_refresh_ist": now_ist.strftime("%Y-%m-%d %I:%M:%S %p IST"),
                "error": str(overall_e)
            }
            return self.last_run_summary
        finally:
            if should_close:
                db.close()

    def _upsert_title_and_relations(self, db: Session, item: dict[str, Any], provider_name: str):
        """Idempotent upsert matching by canonical title and type."""
        canonical = item["canonical_title"]
        t_type = item["type"]
        existing = db.query(Title).filter(
            Title.canonical_title.ilike(canonical),
            Title.type == t_type
        ).first()

        new_source_ids = item.get("source_identifiers", {})

        if existing:
            title = existing
            # Merge source identifiers
            curr_src_ids = json.loads(title.source_identifiers_json or "{}")
            curr_src_ids.update(new_source_ids)
            title.source_identifiers_json = json.dumps(curr_src_ids)

            # Update mutable fields if newer or missing
            if not title.poster_url and item.get("poster_url"):
                title.poster_url = item.get("poster_url")
            if not title.synopsis and item.get("synopsis"):
                title.synopsis = item.get("synopsis")
            if not title.release_date and item.get("release_date"):
                title.release_date = item.get("release_date")
                title.release_year = item.get("release_year")
            if item.get("content_status"):
                title.content_status = item.get("content_status")
            if item.get("runtime_minutes") and not title.runtime_minutes:
                title.runtime_minutes = item.get("runtime_minutes")
            title.updated_at = datetime.utcnow()
        else:
            title = Title(
                canonical_title=canonical,
                original_title=item.get("original_title"),
                alternative_titles_json=json.dumps(item.get("alternative_titles") or []),
                type=t_type,
                original_language=item.get("original_language", "en"),
                release_date=item.get("release_date"),
                release_year=item.get("release_year"),
                country=item.get("country"),
                genres_json=json.dumps(item.get("genres") or []),
                synopsis=item.get("synopsis"),
                content_status=item.get("content_status", "released"),
                franchise=item.get("franchise"),
                poster_url=item.get("poster_url"),
                backdrop_url=item.get("backdrop_url"),
                official_website=item.get("official_website"),
                source_identifiers_json=json.dumps(new_source_ids),
                metadata_completeness=item.get("metadata_completeness", 0.8),
                runtime_minutes=item.get("runtime_minutes"),
                runtime_source=item.get("runtime_source"),
                runtime_verification_status=item.get("runtime_verification_status", "unverified"),
                announced_episodes=item.get("announced_episodes"),
                released_episodes=item.get("released_episodes"),
                known_total_episodes=item.get("known_total_episodes"),
                estimated_total_episodes=item.get("estimated_total_episodes"),
                unknown_total_episodes=item.get("unknown_total_episodes", False)
            )
            db.add(title)
            db.flush() # obtain title.id

        # Upsert ratings with strict provenance
        for r in item.get("ratings", []):
            existing_rating = db.query(Rating).filter(
                Rating.title_id == title.id,
                Rating.source_name == r["source_name"]
            ).first()
            if existing_rating:
                existing_rating.rating_value = r["rating_value"]
                existing_rating.normalized_value = r["normalized_value"]
                existing_rating.vote_count = r.get("vote_count")
                existing_rating.collected_at = datetime.utcnow()
            else:
                db.add(Rating(
                    title_id=title.id,
                    source_name=r["source_name"],
                    rating_value=r["rating_value"],
                    max_rating=r.get("max_rating", 10.0),
                    normalized_value=r["normalized_value"],
                    vote_count=r.get("vote_count"),
                    rating_type=r.get("rating_type", "audience"),
                    source_url=r.get("source_url"),
                    source_identifier=r.get("source_identifier"),
                    collected_at=datetime.utcnow()
                ))

        # Upsert episodes with season and episode numbers
        for ep in item.get("episodes", []):
            existing_ep = db.query(Episode).filter(
                Episode.title_id == title.id,
                Episode.season_number == ep.get("season_number"),
                Episode.episode_number == ep.get("episode_number")
            ).first()
            if not existing_ep:
                db.add(Episode(
                    title_id=title.id,
                    season_number=ep.get("season_number"),
                    episode_number=ep.get("episode_number"),
                    absolute_episode_number=ep.get("absolute_episode_number"),
                    episode_title=ep.get("episode_title"),
                    release_date=ep.get("release_date"),
                    runtime_minutes=ep.get("runtime_minutes"),
                    is_special=ep.get("is_special", False),
                    source=ep.get("source", provider_name),
                    source_identifier=ep.get("source_identifier")
                ))

    def _update_registry_entry(self, db: Session, provider_name: str, success: bool, error_msg: str | None = None):
        entry = db.query(SourceRegistryEntry).filter_by(provider_name=provider_name).first()
        if entry:
            entry.last_sync = datetime.utcnow() if success else entry.last_sync
            entry.last_error = None if success else error_msg
            entry.updated_at = datetime.utcnow()
            db.commit()

pipeline = IngestionPipeline()
