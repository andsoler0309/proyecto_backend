from unittest.mock import patch
import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app


@pytest.fixture(scope="module")
def app_generacion_reportes():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture(scope="module")
def client_generacion_reportes(app_generacion_reportes):
    return app_generacion_reportes.test_client()


@pytest.fixture(scope="module")
def runner_generacion_reportes(app_generacion_reportes):
    return app_generacion_reportes.test_cli_runner()


# Mock requests to external services
@pytest.fixture(autouse=True, scope="module")
def mock_requests():
    with patch("requests.post") as mock_post, patch("requests.get") as mock_get, patch(
        "requests.delete"
    ) as mock_delete:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {}
        mock_delete.return_value.status_code = 200
        yield
