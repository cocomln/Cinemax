from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Title, SourceRegistryEntry
from app.ingestion.pipeline import pipeline
from app.models.schemas import RefreshStatusResponse

router = APIRouter(prefix="/refresh", tags=["Refresh Pipeline"])

@router.post("/trigger")
async def trigger_refresh(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Manually trigger the midnight ingestion and ML recalculation pipeline.
    Runs asynchronously and idempotently.
    """
    background_tasks.add_task(pipeline.run_pipeline)
    return {"status": "started", "message": "Cinemax refresh pipeline initiated in background."}

@router.get("/status", response_model=RefreshStatusResponse)
def get_refresh_status(db: Session = Depends(get_db)):
    total = db.query(Title).count()
    active_sources = [
        e.provider_name for e in db.query(SourceRegistryEntry).filter_by(is_enabled=True).all()
    ]
    summary = pipeline.last_run_summary
    return RefreshStatusResponse(
        status=summary.get("status", "idle"),
        message="Daily refresh runs automatically at 12:00 AM IST (18:30 UTC).",
        last_successful_refresh_ist=summary.get("last_refresh_ist") or "Scheduled for 12:00 AM IST",
        last_successful_refresh_utc=summary.get("last_refresh_utc") or "Scheduled for 18:30 UTC",
        total_titles=total,
        active_sources=active_sources
    )
