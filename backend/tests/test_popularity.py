import pytest
from app.scoring.popularity import PopularityScoringEngine

def test_popularity_bounds_and_weights():
    engine = PopularityScoringEngine()
    res = engine.calculate_popularity(
        recent_mentions=1500,
        prior_mentions=1000,
        total_engagements=6000,
        active_sources_count=3,
        total_possible_sources=4,
        historical_consistency_ratio=0.8
    )
    assert 0.0 <= res["total_score"] <= 100.0
    assert 0.0 <= res["recent_volume_score"] <= 100.0
    assert 0.0 <= res["growth_velocity_score"] <= 100.0
    assert 0.0 <= res["engagement_score"] <= 100.0
    assert 0.0 <= res["source_breadth_score"] <= 100.0
    assert res["has_sufficient_data"] is True
    assert res["status_label"] in ["Trending High", "Popular", "Moderate Activity", "Low Activity"]

def test_missing_data_policy():
    engine = PopularityScoringEngine()
    res = engine.calculate_popularity(
        recent_mentions=0,
        prior_mentions=0,
        total_engagements=0,
        active_sources_count=0
    )
    assert res["total_score"] == 0.0
    assert res["has_sufficient_data"] is False
    assert res["status_label"] == "Insufficient data"
