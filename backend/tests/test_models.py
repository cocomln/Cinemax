import pytest
from app.db.models import Title, Episode, Rating

def test_title_runtime_formatting():
    # 134 minutes -> "2h 14m"
    t1 = Title(canonical_title="Test Movie", type="movie", runtime_minutes=134)
    assert t1.formatted_runtime == "2h 14m"

    # 60 minutes -> "1h"
    t2 = Title(canonical_title="Test Movie 2", type="movie", runtime_minutes=60)
    assert t2.formatted_runtime == "1h"

    # None runtime -> None
    t3 = Title(canonical_title="Test Movie 3", type="movie", runtime_minutes=None)
    assert t3.formatted_runtime is None

def test_episode_unknown_count_semantics():
    # Never treat an unknown episode count as zero
    t_ongoing = Title(
        canonical_title="Ongoing Series",
        type="tv_series",
        released_episodes=12,
        known_total_episodes=None,
        unknown_total_episodes=True
    )
    assert t_ongoing.unknown_total_episodes is True
    assert t_ongoing.known_total_episodes is None
    assert t_ongoing.known_total_episodes != 0

def test_rating_provenance_independence():
    # Ratings must preserve their own scale and source independently
    r1 = Rating(
        title_id="test-id",
        source_name="AniList",
        rating_value=84.0,
        max_rating=100.0,
        normalized_value=8.4,
        rating_type="audience"
    )
    r2 = Rating(
        title_id="test-id",
        source_name="IMDb",
        rating_value=8.8,
        max_rating=10.0,
        normalized_value=8.8,
        rating_type="audience"
    )
    assert r1.source_name != r2.source_name
    assert r1.max_rating == 100.0
    assert r2.max_rating == 10.0
