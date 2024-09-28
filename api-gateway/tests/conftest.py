import pytest
from app import create_app
from unittest.mock import patch


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


# Mock the database session
@pytest.fixture(autouse=True)
def mock_db_session():
    with patch('models.db.session'):
        yield


# Mock requests to external services
@pytest.fixture(autouse=True)
def mock_requests():
    with patch('requests.post') as mock_post, \
            patch('requests.get') as mock_get, \
            patch('requests.delete') as mock_delete:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {}
        mock_delete.return_value.status_code = 200
        yield
