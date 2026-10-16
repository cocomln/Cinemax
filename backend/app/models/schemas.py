from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class RatingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_name: str
    rating_value: float
    max_rating: float
    normalized_value: float
    vote_count: int | None = None
    rating_type: str
    region: str | None = None
    source_url: str | None = None
    source_identifier: str | None = None
    collected_at: datetime


class EpisodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    season_number: int | None = None
    episode_number: int
    absolute_episode_number: int | None = None
    episode_title: str | None = None
    release_date: str | None = None
    runtime_minutes: int | None = None
    is_special: bool
    source: str


class SocialMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    platform: str
    post_count: int
    comment_count: int
    unique_discussions: int
    engagement_count: int
    positive_sentiment: float
    neutral_sentiment: float
    negative_sentiment: float
    mention_velocity: float
    engagement_velocity: float
    source_coverage: float
    observation_window: str
    collected_at: datetime


class HistoricalObservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric_name: str
    metric_value: float
    observation_window: str
    timestamp: datetime
    source: str
    confidence: float
    data_quality_status: str


class PredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title_id: str
    horizon_days: int
    target_metric: str
    current_score: float
    predicted_score: float
    predicted_change: float
    uncertainty_lower: float | None = None
    uncertainty_upper: float | None = None
    model_version: str
    contributing_factors: dict[str, float] = {}
    generated_at: datetime


class TitleSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    canonical_title: str
    original_title: str | None = None
    type: str
    original_language: str | None = None
    release_date: str | None = None
    release_year: int | None = None
    genres: list[str] = []
    content_status: str
    poster_url: str | None = None
    backdrop_url: str | None = None
    current_popularity_score: float | None = 0.0
    popularity_growth_velocity: float | None = 0.0
    popularity_source_coverage: float | None = 0.0
    formatted_runtime: str | None = None


class PopularityScoreBreakdown(BaseModel):
    total_score: float
    recent_volume_score: float
    growth_velocity_score: float
    engagement_score: float
    source_breadth_score: float
    sustained_activity_score: float
    source_coverage: float
    has_sufficient_data: bool
    status_label: str # "Active", "Trending", "Insufficient data"


class TitleDetailResponse(TitleSummaryResponse):
    synopsis: str | None = None
    country: str | None = None
    franchise: str | None = None
    official_website: str | None = None
    runtime_minutes: int | None = None
    runtime_source: str | None = None
    runtime_verification_status: str | None = None
    alternative_titles: list[str] = []
    source_identifiers: dict = {}
    metadata_completeness: float

    # TV / Anime specific counts
    announced_episodes: int | None = None
    released_episodes: int | None = None
    known_total_episodes: int | None = None
    estimated_total_episodes: int | None = None
    unknown_total_episodes: bool = False

    ratings: list[RatingResponse] = []
    episodes: list[EpisodeResponse] = []
    social_metrics: list[SocialMetricResponse] = []
    historical_observations: list[HistoricalObservationResponse] = []
    latest_prediction: PredictionResponse | None = None
    popularity_breakdown: PopularityScoreBreakdown | None = None


class UserPredictionGuessCreate(BaseModel):
    title_id: str
    predicted_score: float = Field(..., ge=0.0, le=100.0)
    user_session_id: str = "anonymous_user"
    horizon_days: int = 7


class UserPredictionGuessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title_id: str
    canonical_title: str | None = None
    user_session_id: str
    predicted_score: float
    baseline_score_at_guess: float
    horizon_days: int
    target_date: datetime
    deadline: datetime
    is_locked: bool
    actual_score: float | None = None
    accuracy_points: float | None = None
    created_at: datetime


class SourceRegistryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    provider_name: str
    provider_type: str
    supported_fields: list[str] = []
    access_method: str
    auth_requirement: str
    cost_status: str
    license_url: str
    attribution_text: str
    rate_limit_info: str
    data_retention_rules: str
    is_enabled: bool
    last_sync: datetime | None = None
    last_error: str | None = None
    coverage_limitations: str


class RefreshStatusResponse(BaseModel):
    status: str
    message: str
    last_successful_refresh_ist: str
    last_successful_refresh_utc: str
    total_titles: int
    active_sources: list[str]
