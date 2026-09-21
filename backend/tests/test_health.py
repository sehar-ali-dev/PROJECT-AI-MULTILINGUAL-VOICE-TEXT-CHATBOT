import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_health_check():
    """Test health check endpoint."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "mock_ai" in data
