import os
import json
from pathlib import Path
from datetime import datetime
from typing import Any
import pandas as pd
from app.ingestion.base import BaseProvider
from app.core.config import settings

class KaggleDatasetImporter(BaseProvider):
    """
    Importer for Kaggle entertainment datasets (CSV, JSON, Parquet).
    Records provenance metadata, publisher attribution, license, and handles schema mapping.
    """

    def __init__(self, datasets_dir: Path | None = None):
        super().__init__(name="Kaggle Dataset Importer", cost_status="Zero-Cost (Free)")
        self.datasets_dir = datasets_dir or (settings.DATA_DIR / "kaggle")
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
        self.catalog_registry_file = self.datasets_dir / "dataset_manifest.json"

    def verify_credentials(self) -> tuple[bool, str]:
        # Local file imports require no credentials. Official Kaggle CLI uses ~/.kaggle/kaggle.json
        kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
        if kaggle_json.exists():
            return True, "Kaggle CLI credentials configured (~/.kaggle/kaggle.json)"
        return True, "Local dataset file import mode active (No credentials needed for local files)"

    def register_dataset_metadata(
        self,
        dataset_name: str,
        original_url: str,
        publisher: str,
        license_name: str,
        coverage_description: str,
        attribution: str,
        known_limitations: str
    ):
        """Record dataset provenance metadata in manifest."""
        manifest = {}
        if self.catalog_registry_file.exists():
            try:
                with open(self.catalog_registry_file, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except Exception:
                manifest = {}

        manifest[dataset_name] = {
            "dataset_name": dataset_name,
            "original_url": original_url,
            "publisher": publisher,
            "license": license_name,
            "retrieval_timestamp": datetime.utcnow().isoformat(),
            "data_coverage": coverage_description,
            "attribution": attribution,
            "known_limitations": known_limitations,
            "last_successful_import": datetime.utcnow().isoformat()
        }

        with open(self.catalog_registry_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    async def fetch_catalog(self, limit: int = 50) -> list[dict[str, Any]]:
        """
        Scan datasets_dir for CSV/JSON/Parquet files and import parsed records.
        """
        imported_titles = []
        try:
            # Check for any CSV files in datasets_dir
            for file_path in self.datasets_dir.glob("*.csv"):
                df = pd.read_csv(file_path)
                # Map common columns
                for _, row in df.head(limit).iterrows():
                    canonical = row.get("title") or row.get("name") or row.get("canonical_title")
                    if not canonical:
                        continue
                    release_year = row.get("release_year") or row.get("year")
                    if pd.isna(release_year):
                        release_year = None
                    else:
                        release_year = int(release_year)

                    imported_titles.append({
                        "canonical_title": str(canonical),
                        "original_title": str(row.get("original_title") or canonical),
                        "alternative_titles": [],
                        "type": str(row.get("type", "movie")),
                        "original_language": str(row.get("original_language", "en")),
                        "release_date": str(row.get("release_date")) if not pd.isna(row.get("release_date")) else None,
                        "release_year": release_year,
                        "country": str(row.get("country", "")),
                        "genres": str(row.get("genres", "")).split(",") if not pd.isna(row.get("genres")) else [],
                        "synopsis": str(row.get("synopsis") or row.get("description", "")),
                        "content_status": "released",
                        "franchise": None,
                        "poster_url": str(row.get("poster_url", "")) if not pd.isna(row.get("poster_url")) else None,
                        "backdrop_url": None,
                        "official_website": None,
                        "source_identifiers": {"kaggle": str(file_path.name)},
                        "metadata_completeness": 0.80,
                        "runtime_minutes": int(row.get("runtime_minutes")) if not pd.isna(row.get("runtime_minutes")) else None,
                        "announced_episodes": None,
                        "released_episodes": None,
                        "known_total_episodes": None,
                        "estimated_total_episodes": None,
                        "unknown_total_episodes": False,
                        "ratings": []
                    })
            self.record_success()
            return imported_titles
        except Exception as e:
            self.record_failure(f"Kaggle import error: {str(e)}")
            return []

    async def fetch_ratings(self, source_id: str) -> list[dict[str, Any]]:
        return []
