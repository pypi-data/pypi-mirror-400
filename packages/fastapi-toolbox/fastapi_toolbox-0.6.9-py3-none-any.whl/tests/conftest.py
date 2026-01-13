import pytest
import os
from unittest.mock import patch


@pytest.fixture(autouse=True)
def reset_database_engine():
    """Reset database engine before each test"""
    import fastapi_toolbox.database as db_module
    db_module._engine = None
    yield
    db_module._engine = None


@pytest.fixture
def temp_env_file(tmp_path):
    """Create a temporary .env file for testing"""
    env_file = tmp_path / ".env"
    return env_file


@pytest.fixture
def mock_env_vars():
    """Fixture to mock environment variables"""
    with patch.dict(os.environ, {}, clear=False):
        yield
