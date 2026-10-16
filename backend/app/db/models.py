import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class Title(Base):
    __tablename__ = "titles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    canonical_title = Column(String(500), nullable=False, index=True)
    original_title = Column(String(500), nullable=True)
    alternative_titles_json = Column(Text, nullable=True, default="[]") # JSON list of strings
    
    # Types: movie, tv_series, anime_series, anime_film, ova, ona, special
    type = Column(String(50), nullable=False, index=True)
    original_language = Column(String(20), nullable=True, default="en")
    release_date = Column(String(30), nullable=True) # YYYY-MM-DD
    release_year = Column(Integer, nullable=True, index=True)
    country = Column(String(100), nullable=True)
    genres_json = Column(Text, nullable=True, default="[]") # JSON list of genres
    synopsis = Column(Text, nullable=True)
    
    # Status: released, ongoing, upcoming, canceled, completed
    content_status = Column(String(50), nullable=False, default="released", index=True)
    franchise = Column(String(255), nullable=True)
    poster_url = Column(String(1000), nullable=True)
    backdrop_url = Column(String(1000), nullable=True)
    official_website = Column(String(1000), nullable=True)
    
    # Provenance source identifiers (e.g. {"anilist": 1, "tvmaze": 2, "wikidata": "Q123"})
    source_identifiers_json = Column(Text, nullable=False, default="{}")
    metadata_completeness = Column(Float, nullable=False, default=0.5)
    
    # Movie specific fields
    runtime_minutes = Column(Integer, nullable=True)
    runtime_source = Column(String(100), nullable=True)
    runtime_verification_status = Column(String(50), nullable=True, default="unverified")
    
    # TV / Anime episode counts with explicit provenance semantics
    announced_episodes = Column(Integer, nullable=True)
    released_episodes = Column(Integer, nullable=True)
    known_total_episodes = Column(Integer, nullable=True)
    estimated_total_episodes = Column(Integer, nullable=True)
    unknown_total_episodes = Column(Boolean, nullable=False, default=False)
    
    # Current computed popularity (0 to 100)
    current_popularity_score = Column(Float, nullable=True, default=0.0)
    popularity_growth_velocity = Column(Float, nullable=True, default=0.0)
    popularity_source_coverage = Column(Float, nullable=True, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    episodes = relationship("Episode", back_populates="title", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="title", cascade="all, delete-orphan")
    social_metrics = relationship("SocialMetric", back_populates="title", cascade="all, delete-orphan")
    historical_observations = relationship("HistoricalObservation", back_populates="title", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="title", cascade="all, delete-orphan")
    arena_guesses = relationship("UserPredictionGuess", back_populates="title", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_titles_type_year", "type", "release_year"),
        Index("idx_titles_status_pop", "content_status", "current_popularity_score"),
    )

    @property
    def formatted_runtime(self) -> str | None:
        if self.runtime_minutes is None or self.runtime_minutes <= 0:
            return None
        hours = self.runtime_minutes // 60
        mins = self.runtime_minutes % 60
        if hours > 0:
            return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
        return f"{mins}m"


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title_id = Column(String(36), ForeignKey("titles.id", ondelete="CASCADE"), nullable=False, index=True)
    season_number = Column(Integer, nullable=True)
    episode_number = Column(Integer, nullable=False)
    absolute_episode_number = Column(Integer, nullable=True)
    episode_title = Column(String(500), nullable=True)
    release_date = Column(String(30), nullable=True)
    runtime_minutes = Column(Integer, nullable=True)
    is_special = Column(Boolean, nullable=False, default=False)
    source = Column(String(100), nullable=False)
    source_identifier = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    title = relationship("Title", back_populates="episodes")

    __table_args__ = (
        Index("idx_episodes_title_season_ep", "title_id", "season_number", "episode_number"),
    )


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title_id = Column(String(36), ForeignKey("titles.id", ondelete="CASCADE"), nullable=False, index=True)
    source_name = Column(String(100), nullable=False) # e.g. "IMDb", "TMDB", "AniList", "MyAnimeList"
    rating_value = Column(Float, nullable=False)
    max_rating = Column(Float, nullable=False, default=10.0) # e.g. 10.0, 100.0, 5.0
    normalized_value = Column(Float, nullable=False) # 0.0 to 10.0 scale for uniform comparisons
    vote_count = Column(Integer, nullable=True)
    rating_type = Column(String(50), nullable=False, default="audience") # audience, critic, editorial
    region = Column(String(20), nullable=True)
    language = Column(String(20), nullable=True)
    source_url = Column(String(1000), nullable=True)
    source_identifier = Column(String(100), nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    title = relationship("Title", back_populates="ratings")

    __table_args__ = (
        Index("idx_ratings_title_source", "title_id", "source_name"),
    )


class SocialMetric(Base):
    __tablename__ = "social_metrics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title_id = Column(String(36), ForeignKey("titles.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String(50), nullable=False) # reddit, x, web, anilist
    post_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    unique_discussions = Column(Integer, nullable=False, default=0)
    engagement_count = Column(Integer, nullable=False, default=0)
    positive_sentiment = Column(Float, nullable=False, default=0.0)
    neutral_sentiment = Column(Float, nullable=False, default=0.0)
    negative_sentiment = Column(Float, nullable=False, default=0.0)
    mention_velocity = Column(Float, nullable=False, default=0.0)
    engagement_velocity = Column(Float, nullable=False, default=0.0)
    source_coverage = Column(Float, nullable=False, default=1.0)
    observation_window = Column(String(20), nullable=False, default="24h")
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    title = relationship("Title", back_populates="social_metrics")

    __table_args__ = (
        Index("idx_social_title_platform", "title_id", "platform", "collected_at"),
    )


class HistoricalObservation(Base):
    __tablename__ = "historical_observations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title_id = Column(String(36), ForeignKey("titles.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False) # popularity_score, mention_count, engagement_rate
    metric_value = Column(Float, nullable=False)
    observation_window = Column(String(20), nullable=False, default="24h")
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    data_quality_status = Column(String(50), nullable=False, default="verified") # verified, estimated, incomplete

    title = relationship("Title", back_populates="historical_observations")

    __table_args__ = (
        Index("idx_hist_title_metric_time", "title_id", "metric_name", "timestamp"),
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title_id = Column(String(36), ForeignKey("titles.id", ondelete="CASCADE"), nullable=False, index=True)
    horizon_days = Column(Integer, nullable=False, default=7)
    target_metric = Column(String(100), nullable=False, default="popularity_score")
    current_score = Column(Float, nullable=False)
    predicted_score = Column(Float, nullable=False)
    predicted_change = Column(Float, nullable=False)
    uncertainty_lower = Column(Float, nullable=True)
    uncertainty_upper = Column(Float, nullable=True)
    model_version = Column(String(100), nullable=False, default="baseline_ridge_v1")
    contributing_factors_json = Column(Text, nullable=False, default="{}") # JSON of top factors
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    title = relationship("Title", back_populates="predictions")


class UserPredictionGuess(Base):
    __tablename__ = "user_prediction_guesses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title_id = Column(String(36), ForeignKey("titles.id", ondelete="CASCADE"), nullable=False, index=True)
    user_session_id = Column(String(100), nullable=False, default="anonymous")
    predicted_score = Column(Float, nullable=False) # 0 to 100
    baseline_score_at_guess = Column(Float, nullable=False)
    horizon_days = Column(Integer, nullable=False, default=7)
    target_date = Column(DateTime, nullable=False)
    deadline = Column(DateTime, nullable=False)
    is_locked = Column(Boolean, nullable=False, default=True)
    actual_score = Column(Float, nullable=True)
    accuracy_points = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    title = relationship("Title", back_populates="arena_guesses")


class SourceRegistryEntry(Base):
    __tablename__ = "source_registry"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    provider_name = Column(String(100), unique=True, nullable=False)
    provider_type = Column(String(50), nullable=False) # catalog, ratings, social, files
    supported_fields_json = Column(Text, nullable=False, default="[]")
    access_method = Column(String(50), nullable=False) # GraphQL, REST, SPARQL, File, etc.
    auth_requirement = Column(String(50), nullable=False, default="None")
    cost_status = Column(String(50), nullable=False, default="Zero-Cost (Free)")
    license_url = Column(String(500), nullable=False)
    attribution_text = Column(Text, nullable=False)
    rate_limit_info = Column(String(200), nullable=False, default="Generous")
    data_retention_rules = Column(Text, nullable=False, default="Public aggregate metrics only")
    is_enabled = Column(Boolean, nullable=False, default=True)
    last_sync = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    coverage_limitations = Column(Text, nullable=False, default="Subject to free endpoint availability")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
