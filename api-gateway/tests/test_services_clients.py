from unittest.mock import patch, MagicMock
from config import Config


def test_create_client_success(client):
    data = {
        "name": "Test Client",
        "email": "test.client@example.com",
        "password": "password123",
        "company_name": "Test Company",
    }
    with patch("requests.post") as mock_post:
        # Mock successful response from Clients service
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"msg": "Client created", "id": "client123"}

        response = client.post("/clients/register", json=data)
        assert response.status_code == 201
        assert response.get_json() == {"msg": "Client created", "id": "client123"}

        # Verify that the request was sent to the correct URL with the correct data
        mock_post.assert_called_with(
            f"{Config.GESTOR_CLIENTES_BASE_URL}/clients/register",
            json=data,
            timeout=5,
        )


def test_create_client_invalid_data(client):
    data = {
        "name": "Test Client",
        "email": "test.client@example.com",
        # Missing 'password' field
        "company_name": "Test Company",
    }
    response = client.post("/clients/register", json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["msg"] == "Invalid data"
    assert "password" in json_data["errors"]


def test_client_login_success(client):
    data = {"email": "test.client@example.com", "password": "password123"}
    with patch("services.clients.requests.post") as mock_post, \
         patch("services.clients.generate_jwt_client") as mock_generate_jwt_client:
        # Mock successful response from Clients service
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id": "client123"}

        # Mock token generation
        mock_generate_jwt_client.return_value = "mocked_token"

        response = client.post("/clients/login", json=data)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["msg"] == "Login successful"
        assert json_data["token"] == "mocked_token"
        assert json_data["client_id"] == "client123"

        # Verify that the request was sent correctly
        mock_post.assert_called_with(
            f"{Config.GESTOR_CLIENTES_BASE_URL}/clients/login",
            json={"email": data["email"], "password": data["password"]},
            timeout=5,
        )


def test_client_login_invalid_data(client):
    data = {"email": "test.client@example.com"}  # Missing 'password'
    response = client.post("/clients/login", json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["msg"] == "Invalid data"
    assert "password" in json_data["errors"]


def test_get_client_success(client):
    client_id = "client123"
    token = "valid_token"
    with patch("auth.decode_jwt") as mock_decode_jwt, \
         patch("auth.is_token_blacklisted") as mock_is_token_blacklisted, \
         patch("services.clients.requests.get") as mock_requests_get:
        # Mock authentication
        mock_decode_jwt.return_value = {"client_id": client_id}
        mock_is_token_blacklisted.return_value = False

        # Mock response from Clients service
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {
            "id": client_id,
            "name": "Test Client",
            "email": "test.client@example.com",
        }

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"/clients/{client_id}", headers=headers)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["id"] == client_id
        assert json_data["name"] == "Test Client"


def test_update_client_plan_success(client):
    client_id = "client123"
    token = "valid_token"
    data = {
        "plan_id": "plan456",
        "email": "test@test.com",
        "company_name": "Test Company",
        "name": "Test Client",
    }
    with patch("auth.decode_jwt") as mock_decode_jwt, \
         patch("auth.is_token_blacklisted") as mock_is_token_blacklisted, \
         patch("services.clients.requests.put") as mock_put:
        # Mock authentication
        mock_decode_jwt.return_value = {"client_id": client_id}
        mock_is_token_blacklisted.return_value = False

        # Mock successful response from Clients service
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = {
            "msg": "Client plan updated",
            "plan_id": "plan456"
        }

        headers = {"Authorization": f"Bearer {token}"}
        response = client.put(f"/clients/{client_id}/plan", json=data, headers=headers)
        assert response.status_code == 200
        assert response.get_json() == {"msg": "Client plan updated", "plan_id": "plan456"}


def test_select_client_plan_success(client):
    client_id = "client123"
    plan_id = "plan456"
    token = "valid_token"
    with patch("auth.decode_jwt") as mock_decode_jwt, \
         patch("auth.is_token_blacklisted") as mock_is_token_blacklisted, \
         patch("services.clients.requests.post") as mock_post:
        # Mock authentication
        mock_decode_jwt.return_value = {"client_id": client_id}
        mock_is_token_blacklisted.return_value = False

        # Mock successful response from Clients service
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"msg": "Plan selected", "plan_id": plan_id}

        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(f"/clients/{client_id}/plan/{plan_id}", headers=headers)
        assert response.status_code == 200
        assert response.get_json() == {"msg": "Plan selected", "plan_id": plan_id}


# def test_get_clients_by_plan_success(client):
#     plan_id = "plan456"
#     with patch("services.clients.requests.get") as mock_get:
#         # Mock successful response from Clients service
#         mock_get.return_value.status_code = 200
#         mock_get.return_value.json.return_value = [
#             {"id": "client123", "name": "Client One", "plan_id": plan_id},
#             {"id": "client456", "name": "Client Two", "plan_id": plan_id},
#         ]

#         response = client.get(f"/clients/plan/{plan_id}")
#         assert response.status_code == 200
#         json_data = response.get_json()
#         assert len(json_data) == 2
#         assert all(client["plan_id"] == plan_id for client in json_data)


def test_get_plans_success(client):
    token = "valid_token"
    with patch("auth.decode_jwt") as mock_decode_jwt, \
         patch("auth.is_token_blacklisted") as mock_is_token_blacklisted, \
         patch("services.clients.requests.get") as mock_get:
        # Mock authentication
        mock_decode_jwt.return_value = {"client_id": "client123"}
        mock_is_token_blacklisted.return_value = False

        # Mock successful response from Clients service
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"plan_id": "plan1", "name": "Basic Plan"},
            {"plan_id": "plan2", "name": "Premium Plan"},
        ]

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/plans", headers=headers)
        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data) == 2
        assert json_data[0]["name"] == "Basic Plan"
