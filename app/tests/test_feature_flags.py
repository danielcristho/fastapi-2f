"""
Feature flag API tests.
Tests CRUD operations and flag evaluation.
"""

import pytest
from fastapi.testclient import TestClient


def test_create_feature_flag():
    """Test creating a feature flag."""
    from main import app
    client = TestClient(app)
    
    flag_data = {
        "key": "test_flag_create",
        "enabled": True,
        "description": "Test feature flag",
        "rules": {
            "strategy": "all"
        }
    }
    
    response = client.post("/api/v1/flags", json=flag_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["key"] == "test_flag_create"
    assert data["enabled"] is True
    assert data["description"] == "Test feature flag"
    assert data["rules"]["strategy"] == "all"


def test_list_feature_flags():
    """Test listing feature flags."""
    from main import app
    client = TestClient(app)
    
    response = client.get("/api/v1/flags")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)


def test_get_nonexistent_feature_flag():
    """Test getting a non-existent feature flag returns 404."""
    from main import app
    client = TestClient(app)
    
    response = client.get("/api/v1/flags/nonexistent_flag")
    assert response.status_code == 404


def test_evaluate_nonexistent_flag():
    """Test evaluating a non-existent feature flag."""
    from main import app
    client = TestClient(app)
    
    response = client.get("/api/v1/flags/nonexistent_flag/evaluate?user_id=test_user")
    assert response.status_code == 200
    
    data = response.json()
    assert data["key"] == "nonexistent_flag"
    assert data["enabled"] is False
    assert data["matched_rule"] == "not_found"
    assert data["source"] == "none"


def test_percentage_rollout_consistency():
    """Test that percentage rollout is consistent for same user."""
    from main import app
    client = TestClient(app)
    
    # Create a flag with 50% rollout
    flag_data = {
        "key": "consistency_flag_test",
        "enabled": True,
        "description": "Consistency test flag",
        "rules": {
            "strategy": "percentage",
            "percentage": 50
        }
    }
    
    create_response = client.post("/api/v1/flags", json=flag_data)
    assert create_response.status_code == 201
    
    # Evaluate multiple times for same user
    user_id = "consistent_user"
    results = []
    
    for _ in range(3):
        response = client.get(f"/api/v1/flags/consistency_flag_test/evaluate?user_id={user_id}")
        assert response.status_code == 200
        results.append(response.json()["enabled"])
    
    # All results should be the same (consistent)
    assert len(set(results)) == 1, "Flag evaluation should be consistent for same user"