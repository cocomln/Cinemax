from datetime import datetime, timedelta
from typing import Any
from sqlalchemy.orm import Session
from app.db.models import UserPredictionGuess, Title

class PredictionArenaService:
    """
    Cinemax Prediction Arena Game Service.
    Enables users to forecast 7-day popularity, lock predictions,
    and earn accuracy points when the target date is reached.
    """

    @staticmethod
    def submit_guess(
        db: Session,
        title_id: str,
        predicted_score: float,
        user_session_id: str = "anonymous",
        horizon_days: int = 7
    ) -> UserPredictionGuess:
        title = db.query(Title).filter_by(id=title_id).first()
        if not title:
            raise ValueError(f"Title {title_id} not found")

        current_score = float(title.current_popularity_score or 0.0)
        now = datetime.utcnow()
        # Submission deadline: locks 12 hours after submission or at midnight
        deadline = now + timedelta(hours=12)
        target_date = now + timedelta(days=horizon_days)

        guess = UserPredictionGuess(
            title_id=title_id,
            user_session_id=user_session_id,
            predicted_score=round(max(0.0, min(100.0, predicted_score)), 1),
            baseline_score_at_guess=current_score,
            horizon_days=horizon_days,
            target_date=target_date,
            deadline=deadline,
            is_locked=True
        )
        db.add(guess)
        db.commit()
        db.refresh(guess)
        return guess

    @staticmethod
    def resolve_completed_guesses(db: Session):
        """
        Evaluate guesses whose target_date has passed against current measured popularity.
        Points awarded = max(0, 100 - (abs(guess - actual) * 3))
        """
        now = datetime.utcnow()
        pending = db.query(UserPredictionGuess).filter(
            UserPredictionGuess.target_date <= now,
            UserPredictionGuess.actual_score.is_(None)
        ).all()

        for g in pending:
            title = db.query(Title).filter_by(id=g.title_id).first()
            if title and title.current_popularity_score is not None:
                actual = float(title.current_popularity_score)
                g.actual_score = actual
                error = abs(g.predicted_score - actual)
                points = max(0.0, round(100.0 - (error * 3.0), 1))
                g.accuracy_points = points
        db.commit()

    @staticmethod
    def get_leaderboard(db: Session, limit: int = 20) -> list[dict[str, Any]]:
        """
        Return leaderboard ranked by total accuracy points and completed predictions.
        """
        from sqlalchemy import func
        results = db.query(
            UserPredictionGuess.user_session_id,
            func.count(UserPredictionGuess.id).label("total_guesses"),
            func.sum(UserPredictionGuess.accuracy_points).label("total_score"),
            func.avg(UserPredictionGuess.accuracy_points).label("avg_accuracy")
        ).filter(
            UserPredictionGuess.accuracy_points.isnot(None)
        ).group_by(
            UserPredictionGuess.user_session_id
        ).order_by(
            func.sum(UserPredictionGuess.accuracy_points).desc()
        ).limit(limit).all()

        leaderboard = []
        for r in results:
            leaderboard.append({
                "user_session_id": r[0],
                "total_guesses": r[1],
                "total_score": round(r[2] or 0.0, 1),
                "avg_accuracy": round(r[3] or 0.0, 1)
            })
        return leaderboard

arena_service = PredictionArenaService()
