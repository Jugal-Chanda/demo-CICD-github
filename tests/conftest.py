import pytest
import os
import tempfile
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from app import app as flask_app
from config import TestingConfig


@pytest.fixture(scope='session')
def app():
    """Create and configure a test app instance."""
    flask_app.config.from_object(TestingConfig)
    return flask_app


@pytest.fixture(scope='session')
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_connection():
    """Create a test database connection."""
    # For testing, we'll use SQLite in-memory database as configured in TestingConfig
    # But we can also test with a real PostgreSQL if needed
    from config import get_config
    config = get_config('testing')

    # For simplicity, we'll skip actual database setup in tests
    # In a real scenario, you'd set up test database here
    yield None


@pytest.fixture(scope='function')
def sample_user_data():
    """Sample user data for testing."""
    return {
        'name': 'Test User',
        'email': 'test@example.com',
        'age': 25
    }


@pytest.fixture(scope='function')
def invalid_user_data():
    """Invalid user data for testing validation."""
    return {
        'name': '',  # Empty name
        'email': 'invalid-email',  # Invalid email
        'age': 'not-a-number'  # Invalid age
    }