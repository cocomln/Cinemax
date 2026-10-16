from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.session import get_db
from app.db.models import UserPredictionGuess, Title
from app.models.schemas import UserPredictionGuessCreate, UserPredictionGuessResponse
from app.arena.game import arena_service

router = APIRouter(prefix="/arena", tags=["Cinemax Prediction Arena"])

@router.post("/predict", response_model=UserPredictionGuessResponse)
def submit_arena_guess(guess_in: UserPredictionGuessCreate, db: Session = Depends(get_db)):
    """Submit a 7-day future popularity guess (0-100) locked upon creation."""
    try:
        guess = arena_service.submit_guess(
            db=db,
            title_id=guess_in.title_id,
            predicted_score=guess_in.predicted_score,
            user_session_id=guess_in.user_session_id,
            horizon_days=guess_in.horizon_days
        )
        title = db.query(Title).filter_by(id=guess.title_id).first()
        res = UserPredictionGuessResponse.model_validate(guess)
        res.canonical_title = title.canonical_title if title else None
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/guesses", response_model=list[UserPredictionGuessResponse])
def get_user_guesses(
    user_session_id: str = Query("anonymous_user"),
    db: Session = Depends(get_db)
):
    """List locked and evaluated guesses for a user session."""
    guesses = db.query(UserPredictionGuess).filter(
        UserPredictionGuess.user_session_id == user_session_id
    ).order_by(desc(UserPredictionGuess.created_at)).all()

    output = []
    for g in guesses:
        title = db.query(Title).filter_by(id=g.title_id).first()
        item = UserPredictionGuessResponse.model_validate(g)
        item.canonical_title = title.canonical_title if title else None
        output.append(item)
    return output

@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db), limit: int = 20):
    """Retrieve ranked Prediction Arena leaderboard."""
    return arena_service.get_leaderboard(db=db, limit=limit)
