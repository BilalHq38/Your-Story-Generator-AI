"""Tests for health check endpoints."""

from fastapi import status


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_root(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "name" in data
        assert "version" in data
        assert "docs" in data

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data
        assert "database" in data

    def test_readiness_check(self, client):
        """Test readiness probe endpoint."""
        response = client.get("/health/ready")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "ready"

    def test_liveness_check(self, client):
        """Test liveness probe endpoint."""
        response = client.get("/health/live")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "alive"
