from unittest.mock import patch, MagicMock
import requests
from config import Config
import datetime


def test_ping(client):
    response = client.get("/api-gateway/ping")
    assert response.status_code == 200
    assert response.get_json() == {"status": "alive"}


def test_login(client):
    data = {"email": "test@example.com", "password": "password123"}
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "id": "agent-id",
            "is_locked": False,
        }
        response = client.post("/agents/login", json=data)
        assert response.status_code == 200
        json_data = response.get_json()
        assert "verification_id" in json_data
        assert "security_question" in json_data


def test_verify_security_answer(client):
    data = {"verification_id": "some-verification-id", "answer": "some-answer"}
    with patch("requests.get") as mock_get, patch(
        "models.Verification.query"
    ) as mock_query:
        mock_verification = mock_query.filter_by.return_value.first.return_value
        mock_verification.agent_id = "agent-id"
        mock_verification.security_question = "Security question?"

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": "agent-id",
            "is_locked": False,
            "role": "agent",
        }

        response = client.post("/agents/verify-security-answer", json=data)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["msg"] == "Login successful"
        assert "token" in json_data
        assert "agent_id" in json_data


def test_create_agent(client):
    data = {
        "name": "Test Agent",
        "email": "test.agent@example.com",
        "password": "password123",
        "role": "agent",
        "identification": "123456789",
        "phone": "555-5555",
        "address": "123 Main St",
        "city": "Testville",
        "state": "Test State",
        "zip_code": "12345",
        "country": "Testland",
    }
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"msg": "Agent created"}

        response = client.post("/agents", json=data)
        assert response.status_code == 201
        assert response.get_json() == {"msg": "Agent created"}


def test_delete_agent(client):
    agent_id = "agent-id"
    with patch("requests.delete") as mock_delete:
        mock_delete.return_value.status_code = 200
        response = client.delete(f"/agents/{agent_id}")
        assert response.status_code == 200
        assert response.get_json() == {"msg": "Agent deleted successfully"}


def test_login_invalid_data(client):
    data = {"email": "test@example.com"}  # Falta el campo 'password'
    response = client.post("/agents/login", json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["msg"] == "Invalid data"
    assert "password" in json_data["errors"]


def test_login_agent_locked(client):
    data = {"email": "locked@example.com", "password": "password123"}
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 403
        response = client.post("/agents/login", json=data)
        assert response.status_code == 403
        assert (
            response.get_json()["msg"]
            == "Your account is locked due to multiple failed attempts. Please contact an administrator."
        )


def test_login_bad_credentials(client):
    data = {"email": "wrong@example.com", "password": "wrongpassword"}
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 401
        response = client.post("/agents/login", json=data)
        assert response.status_code == 401
        assert response.get_json()["msg"] == "Bad username or password"


def test_login_invalid_agent_data(client):
    data = {"email": "test@example.com", "password": "password123"}
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"is_locked": False}  # Falta 'id'
        response = client.post("/agents/login", json=data)
        assert response.status_code == 500
        assert response.get_json()["msg"] == "Invalid agent data received"


def test_login_agent_is_locked(client):
    data = {"email": "test@example.com", "password": "password123"}
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "id": "agent-id",
            "is_locked": True,
        }
        response = client.post("/agents/login", json=data)
        assert response.status_code == 403
        assert (
            response.get_json()["msg"]
            == "Your account is locked due to multiple failed attempts. Please contact an administrator."
        )


def test_login_communication_error(client):
    data = {"email": "test@example.com", "password": "password123"}
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")
        response = client.post("/agents/login", json=data)
        assert response.status_code == 503
        assert response.get_json()["msg"] == "Error communicating with Gestor-Agente"


def test_login_error_fetching_incidents(client):
    data = {"email": "test@example.com", "password": "password123"}
    with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
        # Mock del Gestor-Agente
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "id": "agent-id",
            "is_locked": False,
        }
        # Mock del servicio de incidentes que devuelve error
        mock_get.return_value.status_code = 500
        response = client.post("/agents/login", json=data)
        assert response.status_code == 500
        assert response.get_json()["msg"] == "Error fetching incidents"


def test_verify_security_answer_invalid_data(client):
    data = {"verification_id": "some-verification-id"}  # Falta 'answer'
    response = client.post("/agents/verify-security-answer", json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["msg"] == "Invalid data"
    assert "answer" in json_data["errors"]


def test_verify_security_answer_invalid_verification_id(client):
    data = {"verification_id": "invalid-id", "answer": "some-answer"}
    with patch("models.Verification.query") as mock_query:
        mock_query.filter_by.return_value.first.return_value = None
        response = client.post("/agents/verify-security-answer", json=data)
        assert response.status_code == 400
        assert response.get_json()["msg"] == "Invalid or expired verification ID"


def test_verify_security_answer_agent_not_found(client):
    data = {"verification_id": "valid-id", "answer": "some-answer"}
    with patch("models.Verification.query") as mock_query, patch(
        "requests.get"
    ) as mock_get:
        mock_verification = mock_query.filter_by.return_value.first.return_value
        mock_verification.agent_id = "agent-id"
        mock_verification.security_question = "Security question?"

        # Gestor-Agente devuelve 404
        mock_get.return_value.status_code = 404
        response = client.post("/agents/verify-security-answer", json=data)
        assert response.status_code == 404
        assert response.get_json()["msg"] == "Agent not found"


def test_verify_security_answer_agent_locked(client):
    data = {"verification_id": "valid-id", "answer": "some-answer"}
    with patch("models.Verification.query") as mock_query, patch(
        "requests.get"
    ) as mock_get:
        mock_verification = mock_query.filter_by.return_value.first.return_value
        mock_verification.agent_id = "agent-id"
        mock_verification.security_question = "Security question?"

        # Gestor-Agente devuelve agente bloqueado
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": "agent-id",
            "is_locked": True,
            "role": "agent",
        }
        response = client.post("/agents/verify-security-answer", json=data)
        assert response.status_code == 403
        assert (
            response.get_json()["msg"]
            == "Your account is locked due to multiple failed attempts. Please contact an administrator."
        )


def test_verify_security_answer_error_fetching_incidents(client):
    data = {"verification_id": "valid-id", "answer": "some-answer"}
    with patch("models.Verification.query") as mock_query, patch(
        "requests.get"
    ) as mock_get:
        mock_verification = mock_query.filter_by.return_value.first.return_value
        mock_verification.agent_id = "agent-id"
        mock_verification.security_question = "Security question?"

        mock_get_1 = MagicMock()
        mock_get_1.status_code = 200
        mock_get_1._content = '{"id": "agent-id", "is_locked": false, "role": "agent"}'
        mock_get_1.json.return_value = {
            "id": "agent-id",
            "is_locked": False,
            "role": "agent",
        }

        mock_get_2 = MagicMock()
        mock_get_2.status_code = 500

        # Primera llamada a Gestor-Agente
        mock_get.side_effect = [
            mock_get_1,
            mock_get_2,
        ]

        response = client.post("/agents/verify-security-answer", json=data)
        assert response.status_code == 500
        assert response.get_json()["msg"] == "Error fetching incidents"


def test_logout_missing_token(client):
    response = client.post("/agents/logout")
    assert response.status_code == 401
    assert response.get_json()["msg"] == "Token is missing"


def test_logout_invalid_token(client):
    token = "invalid-token"
    with patch("views.decode_jwt") as mock_decode_jwt:
        mock_decode_jwt.return_value = None
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/agents/logout", headers=headers)
        assert response.status_code == 401
        assert response.get_json()["msg"] == "Invalid or expired token"


def test_delete_agent_communication_error(client):
    agent_id = "agent-id"
    with patch("requests.delete") as mock_delete:
        mock_delete.side_effect = requests.exceptions.RequestException(
            "Connection error"
        )
        response = client.delete(f"/agents/{agent_id}")
        assert response.status_code == 503
        assert response.get_json()["msg"] == "Error communicating with Gestor-Agente"


def test_delete_agent_error_from_gestor(client):
    agent_id = "agent-id"
    with patch("requests.delete") as mock_delete:
        mock_delete.return_value.status_code = 404
        mock_delete.return_value.json.return_value = {"msg": "Agent not found"}
        response = client.delete(f"/agents/{agent_id}")
        assert response.status_code == 404
        assert response.get_json()["msg"] == "Agent not found"
