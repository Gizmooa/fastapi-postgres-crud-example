import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestRootEndpoint:
    def test_root_endpoint_success(self, client: TestClient):
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Notes API"
        assert data["version"] == "0.1.0"
        assert "description" in data
        assert data["docs_url"] == "/docs"
        assert data["health_url"] == "/health"
