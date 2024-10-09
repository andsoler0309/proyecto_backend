# tests/conftest.py

import pytest
from unittest.mock import patch
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


# Mock the database session
@pytest.fixture(autouse=True)
def mock_db_session():
    with patch('models.db.session'):
        yield


# Mock the models and queries
@pytest.fixture(autouse=True)
def mock_models():
    with patch('models.Agent') as MockAgent:
        yield MockAgent


@pytest.fixture(autouse=True)
def mock_views():
    with patch('views.Agent') as MockAgent:
        yield MockAgent