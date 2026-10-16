import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.session import get_db
from app.db.models import Prediction, Title
from app.models.schemas import PredictionResponse

router = APIRouter(prefix="/predictions", tags=["Predictions Engine"])

@router.get("", response_model=list[dict])
def get_predictions(
    db: Session = Depends(get_db),
    sort_by: str = Query("predicted_change", description="Sort by: predicted_change, predicted_score"),
    limit: int = Query(25, ge=1, le=100)
):
    query = db.query(Prediction, Title).join(Title, Prediction.title_id == Title.id)

    if sort_by == "predicted_score":
        query = query.order_by(desc(Prediction.predicted_score))
    else: # predicted_change
        query = query.order_by(desc(Prediction.predicted_change))

    results = query.limit(limit).all()

    output = []
    for pred, title in results:
        factors = {}
        try:
            factors = json.loads(pred.contributing_factors_json or "{}")
        except Exception:
            factors = {}

        output.append({
            "id": pred.id,
            "title_id": title.id,
            "canonical_title": title.canonical_title,
            "type": title.type,
            "poster_url": title.poster_url,
            "current_score": pred.current_score,
            "predicted_score": pred.predicted_score,
            "predicted_change": pred.predicted_change,
            "uncertainty_lower": pred.uncertainty_lower,
            "uncertainty_upper": pred.uncertainty_upper,
            "model_version": pred.model_version,
            "contributing_factors": factors,
            "generated_at": pred.generated_at
        })
    return output
