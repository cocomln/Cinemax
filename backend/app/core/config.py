import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models_store"
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    PROJECT_NAME: str = "Cinemax"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A free, data-driven entertainment intelligence platform for movies, television shows, and anime."
    
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = DATA_DIR
    MODELS_DIR: Path = MODELS_DIR
    
    # Database configuration (Zero-cost: SQLite default, PostgreSQL optional)
    DATABASE_URL: str = os.getenv("DATABASE_URL") if os.getenv("DATABASE_URL") and os.getenv("DATABASE_URL").strip() else f"sqlite:///{BASE_DIR / 'cinemax.db'}"
    
    # Scheduling & Timezone
    TIMEZONE: str = "Asia/Kolkata"
    MIDNIGHT_CRON_UTC: str = "30 18 * * *" # 12:00 AM IST is 18:30 UTC previous day
    
    # Coverage window
    HISTORICAL_COVERAGE_START_YEAR: int = 1995
    
    # Popularity formula component weights (Sum = 1.0)
    WEIGHT_RECENT_VOLUME: float = 0.30
    WEIGHT_GROWTH_VELOCITY: float = 0.25
    WEIGHT_ENGAGEMENT: float = 0.20
    WEIGHT_SOURCE_BREADTH: float = 0.15
    WEIGHT_SUSTAINED_ACTIVITY: float = 0.10
    
    # Optional provider credentials (All zero-cost; features degrade gracefully if missing)
    TMDB_API_KEY: str | None = os.getenv("TMDB_API_KEY", None)
    REDDIT_CLIENT_ID: str | None = os.getenv("REDDIT_CLIENT_ID", None)
    REDDIT_CLIENT_SECRET: str | None = os.getenv("REDDIT_CLIENT_SECRET", None)
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "CinemaxIntelligence/1.0 (Zero-Cost Educational Platform)")
    X_BEARER_TOKEN: str | None = os.getenv("X_BEARER_TOKEN", None)
    
    # ML settings
    PREDICTION_HORIZON_DAYS: int = 7
    MIN_TRAINING_SAMPLES: int = 5

settings = Settings()
