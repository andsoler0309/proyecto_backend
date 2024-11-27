from unittest.mock import patch, MagicMock
import pytest
from flask import Flask
from config import Config


@pytest.mark.parametrize(
    "endpoint, service_url",
    [
        ("/chatbot", f"{Config.SERVICIO_IA_BASE_URL}/chatbot"),
        ("/unified-chatbot", f"{Config.SERVICIO_IA_BASE_URL}/unified-chatbot"),
        ("/chatbot/incident", f"{Config.SERVICIO_IA_BASE_URL}/chatbot/incident"),
    ],
)
def test_chatbot_endpoints(client, endpoint, service_url):
    data = {"message": "Test message"}
    with patch("requests.post") as mock_post:
        # Mock a successful response from the ChatBot service
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"response": "Test response"}

        response = client.post(endpoint, json=data)
        assert response.status_code == 200
        assert response.get_json() == {"response": "Test response"}

        # Verify the request was made to the correct URL with the expected payload
        mock_post.assert_called_with(service_url, json=data, timeout=900)


@pytest.mark.parametrize(
    "endpoint",
    ["/chatbot", "/unified-chatbot", "/chatbot/incident"],
)
def test_chatbot_invalid_data(client, endpoint):
    # Missing required fields in payload
    data = {}
    response = client.post(endpoint, json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["msg"] == "Invalid data"
    assert "errors" in json_data


def test_get_report_insights_languages_success(client):
    client_id = "client123"
    data = {"query": "language data"}
    with patch("requests.post") as mock_post:
        # Mock a successful response from the ChatBot service
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"languages": ["en", "es"]}

        response = client.post(f"/report-languages/{client_id}", json=data)
        assert response.status_code == 200
        assert response.get_json() == {"languages": ["en", "es"]}

        # Verify the request was made to the correct URL with the expected payload
        mock_post.assert_called_with(
            f"{Config.SERVICIO_IA_BASE_URL}/report-languages/{client_id}",
            json=data,
            timeout=900,
        )