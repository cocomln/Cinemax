import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Title, Rating, Episode, SocialMetric, HistoricalObservation, Prediction
from app.models.schemas import (
    TitleDetailResponse, RatingResponse, EpisodeResponse,
    SocialMetricResponse, HistoricalObservationResponse,
    PredictionResponse, PopularityScoreBreakdown
)
from app.scoring.popularity import popularity_engine

router = APIRouter(prefix="/titles", tags=["Title Details"])

@router.get("/{title_id}", response_model=TitleDetailResponse)
def get_title_detail(title_id: str, db: Session = Depends(get_db)):
    title = db.query(Title).filter(Title.id == title_id).first()
    if not title:
        raise HTTPException(status_code=404, detail=f"Title with ID '{title_id}' not found.")

    ratings = db.query(Rating).filter(Rating.title_id == title.id).all()
    episodes = db.query(Episode).filter(Episode.title_id == title.id).order_by(Episode.season_number, Episode.episode_number).all()
    social_metrics = db.query(SocialMetric).filter(SocialMetric.title_id == title.id).all()
    observations = db.query(HistoricalObservation).filter(HistoricalObservation.title_id == title.id).order_by(HistoricalObservation.timestamp.asc()).all()
    prediction = db.query(Prediction).filter(Prediction.title_id == title.id).first()

    # Re-calculate popularity breakdown for transparent inspection
    src_ids = json.loads(title.source_identifiers_json or "{}")
    total_votes = sum(r.vote_count or 100 for r in ratings) if ratings else 100
    recent_mentions = max(40, int(total_votes / 250))
    prior_mentions = max(20, int(recent_mentions * 0.9))

    breakdown_dict = popularity_engine.calculate_popularity(
        recent_mentions=recent_mentions,
        prior_mentions=prior_mentions,
        total_engagements=recent_mentions * 4,
        active_sources_count=max(1, len(src_ids)),
        total_possible_sources=4,
        historical_consistency_ratio=0.75
    )

    pred_resp = None
    if prediction:
        factors = {}
        try:
            factors = json.loads(prediction.contributing_factors_json or "{}")
        except Exception:
            factors = {}

        pred_resp = PredictionResponse(
            id=prediction.id,
            title_id=prediction.title_id,
            horizon_days=prediction.horizon_days,
            target_metric=prediction.target_metric,
            current_score=prediction.current_score,
            predicted_score=prediction.predicted_score,
            predicted_change=prediction.predicted_change,
            uncertainty_lower=prediction.uncertainty_lower,
            uncertainty_upper=prediction.uncertainty_upper,
            model_version=prediction.model_version,
            contributing_factors=factors,
            generated_at=prediction.generated_at
        )

    return TitleDetailResponse(
        id=title.id,
        canonical_title=title.canonical_title,
        original_title=title.original_title,
        type=title.type,
        original_language=title.original_language,
        release_date=title.release_date,
        release_year=title.release_year,
        genres=json.loads(title.genres_json or "[]"),
        content_status=title.content_status,
        poster_url=title.poster_url,
        backdrop_url=title.backdrop_url,
        current_popularity_score=title.current_popularity_score,
        popularity_growth_velocity=title.popularity_growth_velocity,
        popularity_source_coverage=title.popularity_source_coverage,
        formatted_runtime=title.formatted_runtime,
        synopsis=title.synopsis,
        country=title.country,
        franchise=title.franchise,
        official_website=title.official_website,
        runtime_minutes=title.runtime_minutes,
        runtime_source=title.runtime_source,
        runtime_verification_status=title.runtime_verification_status,
        alternative_titles=json.loads(title.alternative_titles_json or "[]"),
        source_identifiers=json.loads(title.source_identifiers_json or "{}"),
        metadata_completeness=title.metadata_completeness,
        announced_episodes=title.announced_episodes,
        released_episodes=title.released_episodes,
        known_total_episodes=title.known_total_episodes,
        estimated_total_episodes=title.estimated_total_episodes,
        unknown_total_episodes=title.unknown_total_episodes,
        ratings=[RatingResponse.model_validate(r) for r in ratings],
        episodes=[EpisodeResponse.model_validate(e) for e in episodes],
        social_metrics=[SocialMetricResponse.model_validate(s) for s in social_metrics],
        historical_observations=[HistoricalObservationResponse.model_validate(o) for o in observations],
        latest_prediction=pred_resp,
        popularity_breakdown=PopularityScoreBreakdown(**breakdown_dict)
    )
