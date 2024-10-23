import pytest
from unittest.mock import patch, MagicMock
from flask import url_for


def test_ping(client_generacion_reportes):
    response = client_generacion_reportes.get("/generacion-reportes/ping")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_generate_report_success(client_generacion_reportes):
    client_id = "client123"

    # Mock de los datos de incidentes
    incident_data = [
        {
            "incident_id": "incident123",
            "agent_id": "agent123",
            "status": "OPEN",
            "registration_medium": "PHONE",
        }
    ]

    # Mock de los datos del cliente
    client_data = {"id": client_id, "name": "Test Client"}

    # Mock de la respuesta del servicio IA
    ia_data = {"analysis": "Análisis de ejemplo"}

    with patch("requests.get") as mock_requests_get, patch(
        "requests.post"
    ) as mock_post:

        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = client_data

        # Mock the incident exists
        mock_incident_response = MagicMock()
        mock_incident_response.status_code = 200
        mock_incident_response.json.return_value = incident_data
        mock_requests_get.side_effect = [
            mock_incident_response,
            mock_requests_get.return_value,
        ]

        # Configurar mock para requests.post (servicio IA)
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = ia_data

        response = client_generacion_reportes.get(f"/reports/{client_id}")
        assert response.status_code == 200
        data = response.get_json()

        assert data["client"] == client_data
        assert data["incidents"] == incident_data
        assert data["stats"]["total_incidents"] == 1
        assert data["stats"]["total_open_incidents"] == 1
        assert data["stats"]["total_closed_incidents"] == 0
        assert "average_resolution_time" in data["stats"]


def test_generate_report_incident_service_failure(client_generacion_reportes):
    client_id = "client123"

    with patch("requests.get") as mock_get:
        # Simular fallo en el servicio de incidentes
        mock_get.return_value.status_code = 500
        mock_get.return_value.json.return_value = {"error": "Internal Server Error"}

        response = client_generacion_reportes.get(f"/reports/{client_id}")
        assert response.status_code == 500
        assert response.get_json() == {"error": "Internal Server Error"}


# Función auxiliar para crear una respuesta mock
def create_mock_response(status_code, json_data):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    return mock_resp
