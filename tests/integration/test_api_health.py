import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestHealthCheck:
    def test_health_check_success(self, client: TestClient):
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["message"] == "API is running"
        assert "status" in data
        assert "message" in data

    def test_detailed_health_check_success(self, client: TestClient):
        """Test successful detailed health check with database."""
        response = client.get("/health/detailed")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert (
            "database" in data["message"].lower()
            or "running" in data["message"].lower()
        )
