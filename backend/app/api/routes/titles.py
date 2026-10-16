import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.db.session import get_db
from app.db.models import Title
from app.models.schemas import TitleSummaryResponse

router = APIRouter(prefix="/titles", tags=["Titles"])

@router.get("", response_model=list[TitleSummaryResponse])
def get_titles(
    db: Session = Depends(get_db),
    type: str | None = Query(None, description="Filter by title type (e.g. movie, tv_series, anime_series)"),
    status: str | None = Query(None, description="Filter by content status (e.g. released, ongoing, upcoming)"),
    year_from: int | None = Query(1995, description="Filter by start release year"),
    year_to: int | None = Query(None, description="Filter by end release year"),
    genre: str | None = Query(None, description="Filter by genre"),
    search: str | None = Query(None, description="Search by title keyword"),
    sort_by: str = Query("popularity", description="Sort by: popularity, velocity, release_date, rating"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    query = db.query(Title)

    if type:
        if type == "anime":
            query = query.filter(Title.type.like("anime%"))
        elif type == "tv":
            query = query.filter(Title.type == "tv_series")
        elif type == "movie":
            query = query.filter(Title.type.in_(["movie", "anime_film"]))
        else:
            query = query.filter(Title.type == type)

    if status:
        query = query.filter(Title.content_status == status)

    if year_from:
        query = query.filter(Title.release_year >= year_from)
    if year_to:
        query = query.filter(Title.release_year <= year_to)

    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            (Title.canonical_title.ilike(search_fmt)) |
            (Title.original_title.ilike(search_fmt)) |
            (Title.alternative_titles_json.ilike(search_fmt))
        )

    if genre:
        query = query.filter(Title.genres_json.ilike(f"%{genre}%"))

    # Sorting
    if sort_by == "velocity":
        query = query.order_by(desc(Title.popularity_growth_velocity), desc(Title.current_popularity_score))
    elif sort_by == "release_date":
        query = query.order_by(desc(Title.release_date))
    else: # popularity
        query = query.order_by(desc(Title.current_popularity_score))

    titles = query.offset(offset).limit(limit).all()

    results = []
    for t in titles:
        results.append(TitleSummaryResponse(
            id=t.id,
            canonical_title=t.canonical_title,
            original_title=t.original_title,
            type=t.type,
            original_language=t.original_language,
            release_date=t.release_date,
            release_year=t.release_year,
            genres=json.loads(t.genres_json or "[]"),
            content_status=t.content_status,
            poster_url=t.poster_url,
            backdrop_url=t.backdrop_url,
            current_popularity_score=t.current_popularity_score,
            popularity_growth_velocity=t.popularity_growth_velocity,
            popularity_source_coverage=t.popularity_source_coverage,
            formatted_runtime=t.formatted_runtime
        ))
    return results

@router.get("/trending", response_model=list[TitleSummaryResponse])
def get_trending_titles(db: Session = Depends(get_db), limit: int = 10):
    """Return top trending titles by recent popularity score."""
    return get_titles(db=db, sort_by="popularity", limit=limit, offset=0)

@router.get("/breakouts", response_model=list[TitleSummaryResponse])
def get_breakout_titles(db: Session = Depends(get_db), limit: int = 10):
    """Return titles with highest mention and popularity velocity."""
    return get_titles(db=db, sort_by="velocity", limit=limit, offset=0)

@router.get("/upcoming", response_model=list[TitleSummaryResponse])
def get_upcoming_titles(db: Session = Depends(get_db), limit: int = 10):
    """Return announced upcoming titles."""
    return get_titles(db=db, status="upcoming", sort_by="popularity", limit=limit, offset=0)
