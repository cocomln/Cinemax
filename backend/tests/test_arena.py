import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from app.db.models import Title, UserPredictionGuess
from app.arena.game import arena_service

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def test_prediction_arena_submission_and_scoring(test_db):
    title = Title(
        canonical_title="Arena Test Show",
        type="tv_series",
        current_popularity_score=60.0
    )
    test_db.add(title)
    test_db.commit()

    # Submit user guess of 65.0
    guess = arena_service.submit_guess(
        db=test_db,
        title_id=title.id,
        predicted_score=65.0,
        user_session_id="user_alpha",
        horizon_days=7
    )
    assert guess.is_locked is True
    assert guess.predicted_score == 65.0
    assert guess.baseline_score_at_guess == 60.0

    # Simulate target arrival: title popularity reaches 64.0
    title.current_popularity_score = 64.0
    test_db.commit()

    # Force target_date into the past for test resolution
    from datetime import datetime, timedelta
    guess.target_date = datetime.utcnow() - timedelta(days=1)
    test_db.commit()

    arena_service.resolve_completed_guesses(test_db)
    test_db.refresh(guess)

    assert guess.actual_score == 64.0
    # Error = |65 - 64| = 1.0. Points = 100 - (1.0 * 3) = 97.0
    assert guess.accuracy_points == 97.0
