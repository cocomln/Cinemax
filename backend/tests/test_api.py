import pytest
from fastapi.testclient import TestClient
from main import app
from app.db.init_db import init_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Cinemax"

def test_source_registry_endpoint():
    response = client.get("/api/sources")
    assert response.status_code == 200
    sources = response.json()
    assert len(sources) >= 5
    provider_names = [s["provider_name"] for s in sources]
    assert "AniList" in provider_names
    assert "TVmaze" in provider_names
    assert "Wikidata" in provider_names

def test_titles_endpoint():
    response = client.get("/api/titles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_refresh_status_endpoint():
    response = client.get("/api/refresh/status")
    assert response.status_code == 200
    data = response.json()
    assert "12:00 AM IST" in data["message"]
