"""
Health endpoint tests.
Tests all Kubernetes health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_health_live():
    """Test liveness endpoint returns 200."""
    from main import app
    client = TestClient(app)
    
    response = client.get("/health/live")
    assert response.status_code == 200
    assert "fastapi-eks" in response.text
    assert "1.0.0" in response.text
    assert "App:" in response.text
    assert "Version:" in response.text


def test_health_ready():
    """Test readiness endpoint returns 200."""
    from main import app
    client = TestClient(app)
    
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert "fastapi-eks" in response.text


def test_health_startup():
    """Test startup endpoint returns 200."""
    from main import app
    client = TestClient(app)
    
    response = client.get("/health/startup")
    assert response.status_code == 200
    assert "fastapi-eks" in response.text
    assert "1.0.0" in response.text
    assert "App:" in response.text
    assert "Version:" in response.text


def test_root_redirect():
    """Test root endpoint redirects to /docs."""
    from main import app
    client = TestClient(app)
    
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test_api_info():
    """Test API info endpoint."""
    from main import app
    client = TestClient(app)
    
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    
    data = response.json()
    assert data["app_name"] == "fastapi-eks"
    assert data["version"] == "1.0.0"
    assert data["environment"] == "development"
    assert "redis_enabled" in data
    assert "redis_connected" in data


def test_ping():
    """Test ping endpoint."""
    from main import app
    client = TestClient(app)
    
    response = client.get("/api/v1/ping")
    assert response.status_code == 200
    
    data = response.json()
    assert data["message"] == "pong"
    assert data["version"] == "1.0.0"