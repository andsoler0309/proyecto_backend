import json
from unittest.mock import patch, MagicMock
import datetime


def test_create_incident(client):
    # Mock the token_required decorator and provide a current_agent
    with patch("auth.decode_jwt") as mock_decode_jwt, patch(
        "auth.is_token_blacklisted"
    ) as mock_is_token_blacklisted, patch("requests.post") as mock_requests_post, patch(
        "models.Session.query"
    ) as mock_session_query, patch(
        "requests.get"
    ) as mock_requests_get:

        # Set up the mocks
        mock_decode_jwt.return_value = {
            "agent_id": "agent123",
            "jti": "jti123",
            "session_id": "session123",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            "iat": datetime.datetime.utcnow(),
        }
        mock_is_token_blacklisted.return_value = False

        mock_session = mock_session_query.filter_by.return_value.first.return_value
        mock_session.last_activity = datetime.datetime.utcnow() - datetime.timedelta(
            minutes=5
        )

        mock_requests_post.return_value.status_code = 201
        mock_requests_post.return_value.json.return_value = {
            "incident_id": "incident123",
            "agent_id": "agent123",
            "description": "Test incident",
            "date": "2023-01-01",
        }

        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {
            "id": "agent123",
            "role": "AGENT",
        }

        data = {
            "agent_id": "agent123",
            "description": "Test incident",
            "date": "2023-01-01",
            "registration_medium": "phone",
            "user_id": 1234,
            "client_id": "client123",
        }

        headers = {"Authorization": "Bearer valid_token"}
        response = client.post("/incidents", json=data, headers=headers)

        assert response.status_code == 201
        assert response.get_json()["incident_id"] == "incident123"


def test_create_incident_unauthorized_agent(client):
    # Test when agent_id in data does not match current_agent['id']
    with patch("auth.decode_jwt") as mock_decode_jwt, patch(
        "auth.is_token_blacklisted"
    ) as mock_is_token_blacklisted, patch(
        "models.Session.query"
    ) as mock_session_query, patch(
        "requests.get"
    ) as mock_requests_get:

        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {
            "id": "agent123",
            "role": "AGENT",
        }

        mock_session = mock_session_query.filter_by.return_value.first.return_value
        mock_session.last_activity = datetime.datetime.utcnow() - datetime.timedelta(
            minutes=5
        )

        mock_decode_jwt.return_value = {
            "agent_id": "agent123",
            "jti": "jti123",
            "session_id": "session123",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            "iat": datetime.datetime.utcnow(),
        }
        mock_is_token_blacklisted.return_value = False

        # Prepare test data with different agent_id
        data = {
            "agent_id": "agent456",
            "description": "Test incident",
            "date": "2023-01-01",
            "registration_medium": "email",
            "user_id": 1234,
            "client_id": "client123",
        }

        headers = {"Authorization": "Bearer valid_token"}
        response = client.post("/incidents", json=data, headers=headers)

        assert response.status_code == 403
        assert response.get_json()["msg"] == "Cannot create incident for another agent"


def test_delete_incident(client):
    # Test delete incident with admin role
    with patch("auth.jwt.decode") as mock_jwt_decode, patch(
        "requests.get"
    ) as mock_requests_get, patch("requests.delete") as mock_requests_delete, patch(
        "models.Session.query"
    ) as mock_session_query:

        mock_session = mock_session_query.filter_by.return_value.first.return_value
        mock_session.last_activity = datetime.datetime.utcnow() - datetime.timedelta(
            minutes=5
        )
        mock_jwt_decode.return_value = {"agent_id": "admin123"}
        # Mock the agent has admin role
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {
            "id": "admin123",
            "role": "ADMIN",
        }

        # Mock the incident exists
        mock_incident_response = MagicMock()
        mock_incident_response.status_code = 200
        mock_incident_response.json.return_value = {
            "incident_id": "incident123",
            "agent_id": "agent123",
        }
        mock_requests_get.side_effect = [
            mock_requests_get.return_value,
            mock_incident_response,
        ]

        # Mock delete response
        mock_requests_delete.return_value.status_code = 200

        headers = {"Authorization": "Bearer valid_token"}
        response = client.delete("/incidents/incident123", headers=headers)

        assert response.status_code == 200
        assert response.get_json()["msg"] == "Incident deleted successfully"


def test_delete_incident_non_admin(client):
    # Test delete incident with non-admin role
    with patch("auth.jwt.decode") as mock_jwt_decode, patch(
        "requests.get"
    ) as mock_requests_get:

        mock_jwt_decode.return_value = {"agent_id": "agent123"}
        # Mock the agent has non-admin role
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {
            "id": "agent123",
            "role": "AGENT",
        }

        headers = {"Authorization": "Bearer valid_token"}
        response = client.delete("/incidents/incident123", headers=headers)

        assert response.status_code == 403
        assert "Access denied" in response.get_json()["msg"]


def test_get_incident_detail(client):
    with patch("requests.get") as mock_requests_get:
        # Mock incident detail response
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {
            "incident_id": "incident123",
            "agent_id": "agent123",
            "description": "Test incident",
            "date": "2023-01-01",
        }

        response = client.get("/incidents/incident123")

        assert response.status_code == 200
        assert response.get_json()["incident_id"] == "incident123"


def test_get_incidents_by_user(client):
    with patch("requests.get") as mock_requests_get:
        # Mock incidents list response
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = [
            {
                "incident_id": "incident123",
                "agent_id": "agent123",
                "description": "Test incident",
                "date": "2023-01-01",
            },
            {
                "incident_id": "incident456",
                "agent_id": "agent123",
                "description": "Another incident",
                "date": "2023-01-02",
            },
        ]

        response = client.get("/incidents/user/user123")

        assert response.status_code == 200
        assert len(response.get_json()) == 2


def test_update_incident(client):
    # Test updating an incident
    with patch("auth.decode_jwt") as mock_decode_jwt, patch(
        "auth.is_token_blacklisted"
    ) as mock_is_token_blacklisted, patch("requests.get") as mock_requests_get, patch(
        "models.Session.query"
    ) as mock_session_query, patch(
        "requests.put"
    ) as mock_requests_put:

        mock_session = mock_session_query.filter_by.return_value.first.return_value
        mock_session.last_activity = datetime.datetime.utcnow() - datetime.timedelta(
            minutes=5
        )

        mock_decode_jwt.return_value = {
            "agent_id": "agent123",
            "jti": "jti123",
            "session_id": "session123",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            "iat": datetime.datetime.utcnow(),
        }
        mock_is_token_blacklisted.return_value = False

        # Mock the GET request to get the incident
        mock_get_incident_response = MagicMock()
        mock_get_incident_response.status_code = 200
        mock_get_incident_response.json.return_value = {
            "incident_id": "incident123",
            "agent_id": "agent123",
            "description": "Old description",
        }
        mock_requests_get.return_value = mock_get_incident_response

        # Mock the PUT request to update the incident
        mock_requests_put.return_value.status_code = 200
        mock_requests_put.return_value.json.return_value = {
            "incident_id": "incident123",
            "agent_id": "agent123",
            "description": "Updated description",
        }

        # Prepare test data
        data = {
            "description": "Updated description",
            "registration_medium": "email",
            "user_id": 1234,
            "agent_id": "agent123",
            "date": "2023-01-01",
            "status": "closed",
        }

        headers = {"Authorization": "Bearer valid_token"}
        response = client.put("/incidents/incident123", json=data, headers=headers)

        assert response.status_code == 200
        assert response.get_json()["description"] == "Updated description"


def test_get_incident_possible_solution(client):
    with patch("requests.get") as mock_requests_get:
        # Mock possible solution response
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {
            "incident_id": "incident123",
            "possible_solution": "Restart the device",
        }

        response = client.get("/incidents/incident123/solution")

        assert response.status_code == 200
        assert response.get_json()["possible_solution"] == "Restart the device"
