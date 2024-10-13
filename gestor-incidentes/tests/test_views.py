from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError


def test_ping(client):
    response = client.get("/gestor-incidentes/ping")
    assert response.status_code == 200
    assert response.get_json() == {"status": "alive"}


def test_create_incident_invalid_data(client):
    data = {
        "registration_medium": "phone",
        "user_id": 1234,
        "agent_id": "agent123",
        "client_id": "client123",
    }
    response = client.post("/incidents", json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert "Invalid data" in json_data["msg"]


def test_create_incident_missing_agent_id(client):
    data = {
        "description": "Test incident",
        "date": "2023-01-01",
        "registration_medium": "email",
        "user_id": 1234,
        "client_id": "client123",
    }
    response = client.post("/incidents", json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["msg"] == "Invalid data"


def test_create_incident_invalid_registration_medium(client):
    data = {
        "description": "Test incident",
        "date": "2023-01-01",
        "registration_medium": "invalid_medium",
        "user_id": 1234,
        "agent_id": "agent123",
        "client_id": "client123",
    }
    response = client.post("/incidents", json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["msg"] == "Invalid data"


def test_create_incident_db_error(client):
    data = {
        "description": "Test incident",
        "date": "2023-01-01",
        "registration_medium": "PHONE",
        "user_id": 1234,
        "agent_id": "agent123",
        "client_id": "client123",
    }

    with patch("views.Incident") as MockIncident, patch(
        "views.db.session"
    ) as mock_session:

        mock_incident_instance = MagicMock()
        MockIncident.return_value = mock_incident_instance

        mock_session.commit.side_effect = IntegrityError(
            "Mock IntegrityError", None, None
        )

        response = client.post("/incidents", json=data)
        assert response.status_code == 500
        json_data = response.get_json()
        assert json_data["msg"] == "Error creating incident"


def test_get_incident_detail_not_found(client):
    incident_id = "incident123"
    with patch("views.Incident") as MockIncident:
        MockIncident.query.get.return_value = None

        response = client.get(f"/incidents/{incident_id}")
        assert response.status_code == 404
        json_data = response.get_json()
        assert json_data["msg"] == "Incident not found"


def test_delete_incident_success(client):
    incident_id = "incident123"
    with patch("views.Incident") as MockIncident, patch(
        "views.db.session"
    ) as mock_session:

        mock_incident_instance = MagicMock()
        MockIncident.query.get.return_value = mock_incident_instance

        response = client.delete(f"/incidents/{incident_id}")
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["msg"] == "Incident deleted"

        mock_session.delete.assert_called_with(mock_incident_instance)
        mock_session.commit.assert_called()


def test_delete_incident_not_found(client):
    incident_id = "incident123"
    with patch("views.Incident") as MockIncident:
        MockIncident.query.get.return_value = None

        response = client.delete(f"/incidents/{incident_id}")
        assert response.status_code == 404
        json_data = response.get_json()
        assert json_data["msg"] == "Incident not found"


def test_update_incident_invalid_data(client):
    incident_id = "incident123"
    data = {"user_id": 1234, "agent_id": "agent123", "status": "closed"}
    response = client.put(f"/incidents/{incident_id}", json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert "Invalid data" in json_data["msg"]


def test_update_incident_not_found(client):
    incident_id = "incident123"
    data = {
        "description": "Updated incident",
        "date": "2023-02-01",
        "registration_medium": "email",
        "user_id": 1234,
        "agent_id": "agent123",
        "status": "closed",
    }
    with patch("views.Incident") as MockIncident:
        MockIncident.query.get.return_value = None

        response = client.put(f"/incidents/{incident_id}", json=data)
        assert response.status_code == 404
        json_data = response.get_json()
        assert json_data["msg"] == "Incident not found"


def test_update_incident_invalid_registration_medium(client):
    incident_id = "incident123"
    data = {
        "description": "Updated incident",
        "date": "2023-02-01",
        "registration_medium": "invalid_medium",
        "user_id": 1234,
        "agent_id": "agent123",
        "status": "closed",
    }

    with patch("views.Incident") as MockIncident:
        mock_incident_instance = MagicMock()
        MockIncident.query.get.return_value = mock_incident_instance

        response = client.put(f"/incidents/{incident_id}", json=data)
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data["msg"] == "Invalid data"


def test_update_incident_invalid_status(client):
    incident_id = "incident123"
    data = {
        "description": "Updated incident",
        "date": "2023-02-01",
        "registration_medium": "email",
        "user_id": 1234,
        "agent_id": "agent123",
        "status": "invalid_status",
    }
    with patch("views.Incident") as MockIncident:
        mock_incident_instance = MagicMock()
        MockIncident.query.get.return_value = mock_incident_instance

        response = client.put(f"/incidents/{incident_id}", json=data)
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data["msg"] == "Invalid data"


def test_get_incident_possible_solution_not_found(client):
    incident_id = "incident123"
    with patch("views.Incident") as MockIncident:
        MockIncident.query.get.return_value = None

        response = client.get(f"/incidents/{incident_id}/solution")
        assert response.status_code == 404
        json_data = response.get_json()
        assert json_data["msg"] == "Incident not found"
