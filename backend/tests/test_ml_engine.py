import pytest
from app.ml.engine import PredictionEngine
from app.db.models import Title

def test_ml_prediction_bounds_and_uncertainty():
    engine = PredictionEngine()
    title = Title(
        canonical_title="Dune 3",
        type="movie",
        content_status="upcoming",
        current_popularity_score=68.5,
        popularity_growth_velocity=15.0,
        popularity_source_coverage=0.8,
        release_date="2026-12-01"
    )

    pred = engine.predict_7d(title)
    assert 0.0 <= pred["predicted_score"] <= 100.0
    assert pred["uncertainty_lower"] <= pred["predicted_score"] <= pred["uncertainty_upper"]
    assert "model_version" in pred
    assert len(pred["contributing_factors"]) > 0
