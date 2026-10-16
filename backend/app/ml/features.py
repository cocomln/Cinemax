from datetime import datetime
import numpy as np
import pandas as pd

def extract_title_features(title, historical_observations=None, social_metrics=None) -> dict[str, float]:
    """
    Extract time-consistent features for ML prediction without data leakage.
    """
    now = datetime.utcnow()
    
    # Days since or until release
    days_to_release = 0.0
    if title.release_date:
        try:
            parts = [int(p) for p in title.release_date.split("-")]
            if len(parts) == 3:
                rel_dt = datetime(parts[0], parts[1], parts[2])
                days_to_release = (rel_dt - now).total_seconds() / 86400.0
            elif len(parts) == 1:
                rel_dt = datetime(parts[0], 1, 1)
                days_to_release = (rel_dt - now).total_seconds() / 86400.0
        except Exception:
            days_to_release = 0.0

    is_upcoming = 1.0 if title.content_status == "upcoming" or days_to_release > 0 else 0.0
    is_ongoing = 1.0 if title.content_status == "ongoing" else 0.0
    is_movie = 1.0 if title.type in ["movie", "anime_film"] else 0.0
    is_anime = 1.0 if "anime" in title.type else 0.0

    current_score = float(title.current_popularity_score or 0.0)
    velocity = float(title.popularity_growth_velocity or 0.0)
    coverage = float(title.popularity_source_coverage or 0.5)

    # Social metrics summary if present
    post_count = 0.0
    engagement_rate = 0.0
    pos_sentiment = 0.0
    if social_metrics:
        total_posts = sum(m.post_count for m in social_metrics)
        total_eng = sum(m.engagement_count for m in social_metrics)
        post_count = float(total_posts)
        engagement_rate = float(total_eng) / max(1.0, post_count)
        if social_metrics:
            pos_sentiment = float(sum(m.positive_sentiment for m in social_metrics) / len(social_metrics))

    # Historical trend
    hist_change_7d = 0.0
    if historical_observations and len(historical_observations) >= 2:
        sorted_obs = sorted(historical_observations, key=lambda x: x.timestamp)
        hist_change_7d = sorted_obs[-1].metric_value - sorted_obs[0].metric_value

    return {
        "current_score": current_score,
        "velocity": velocity,
        "coverage": coverage,
        "days_to_release": days_to_release,
        "is_upcoming": is_upcoming,
        "is_ongoing": is_ongoing,
        "is_movie": is_movie,
        "is_anime": is_anime,
        "post_count": post_count,
        "engagement_rate": engagement_rate,
        "pos_sentiment": pos_sentiment,
        "hist_change_7d": hist_change_7d
    }

FEATURE_NAMES = [
    "current_score",
    "velocity",
    "coverage",
    "days_to_release",
    "is_upcoming",
    "is_ongoing",
    "is_movie",
    "is_anime",
    "post_count",
    "engagement_rate",
    "pos_sentiment",
    "hist_change_7d"
]
