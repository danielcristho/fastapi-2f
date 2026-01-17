import pytest
import os
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["ENVIRONMENT"] = "development"
    os.environ["REDIS_ENABLED"] = "false"
    os.environ["SSM_ENABLED"] = "false"
    os.environ["LOG_LEVEL"] = "WARNING"


@pytest.fixture
def client():
    """Create test client."""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def sample_flag_data():
    """Sample flag data for testing."""
    return {
        "key": "sample_flag",
        "enabled": True,
        "description": "Sample feature flag for testing",
        "rules": {
            "strategy": "all"
        },
        "metadata": {
            "team": "test",
            "environment": "test"
        }
    }


@pytest.fixture
def percentage_flag_data():
    """Percentage rollout flag data for testing."""
    return {
        "key": "percentage_flag",
        "enabled": True,
        "description": "Percentage rollout flag",
        "rules": {
            "strategy": "percentage",
            "percentage": 25
        }
    }


@pytest.fixture
def user_list_flag_data():
    """User list flag data for testing."""
    return {
        "key": "user_list_flag",
        "enabled": True,
        "description": "User list flag",
        "rules": {
            "strategy": "user_list",
            "user_ids": ["user1", "user2", "user3"]
        }
    }