from abc import ABC, abstractmethod
from typing import Any
import httpx
from datetime import datetime

class BaseProvider(ABC):
    """
    Abstract base adapter for all Cinemax data ingestion providers.
    Ensures modularity, rate-limit awareness, error isolation, and provenance tracking.
    """

    def __init__(self, name: str, cost_status: str = "Zero-Cost (Free)"):
        self.name = name
        self.cost_status = cost_status
        self.last_sync: datetime | None = None
        self.last_error: str | None = None
        self.is_enabled: bool = True

    @abstractmethod
    async def fetch_catalog(self, limit: int = 50) -> list[dict[str, Any]]:
        """Fetch title metadata records from the provider."""
        pass

    @abstractmethod
    async def fetch_ratings(self, source_id: str) -> list[dict[str, Any]]:
        """Fetch rating data with explicit provenance."""
        pass

    @abstractmethod
    def verify_credentials(self) -> tuple[bool, str]:
        """Verify whether required zero-cost credentials are present and valid."""
        pass

    def record_success(self):
        self.last_sync = datetime.utcnow()
        self.last_error = None

    def record_failure(self, error_msg: str):
        self.last_error = error_msg
