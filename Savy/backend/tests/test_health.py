"""
Tests for health check and root endpoints.
"""

def test_health_check(test_client):
    """Test the /health endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data

def test_root_endpoint(test_client):
    """Test the root / endpoint."""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Savy API" in data["message"]
    assert "docs_url" in data
    assert "health_url" in data
