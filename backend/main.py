from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.init_db import init_db
from app.api.routes.titles import router as titles_router
from app.api.routes.detail import router as detail_router
from app.api.routes.predictions import router as predictions_router
from app.api.routes.arena import router as arena_router
from app.api.routes.sources import router as sources_router
from app.api.routes.refresh import router as refresh_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables and seed Source Registry
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(titles_router, prefix="/api")
app.include_router(detail_router, prefix="/api")
app.include_router(predictions_router, prefix="/api")
app.include_router(arena_router, prefix="/api")
app.include_router(sources_router, prefix="/api")
app.include_router(refresh_router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timezone": settings.TIMEZONE,
        "midnight_schedule_utc": settings.MIDNIGHT_CRON_UTC
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
