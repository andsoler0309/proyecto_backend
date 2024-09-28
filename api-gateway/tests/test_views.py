import json
from unittest.mock import patch


def test_ping(client):
    response = client.get('/api-gateway/ping')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'alive'}


def test_login(client):
    data = {
        "email": "test@example.com",
        "password": "password123"
    }
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'id': 'agent-id',
            'is_locked': False
        }
        response = client.post('/agents/login', json=data)
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'verification_id' in json_data
        assert 'security_question' in json_data


def test_verify_security_answer(client):
    data = {
        "verification_id": "some-verification-id",
        "answer": "some-answer"
    }
    with patch('requests.get') as mock_get, \
            patch('models.Verification.query') as mock_query:
        mock_verification = mock_query.filter_by.return_value.first.return_value
        mock_verification.agent_id = 'agent-id'
        mock_verification.security_question = 'Security question?'

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'id': 'agent-id',
            'is_locked': False,
            'role': 'agent'
        }

        response = client.post('/agents/verify-security-answer', json=data)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['msg'] == 'Login successful'
        assert 'token' in json_data
        assert 'agent_id' in json_data


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
        "country": "Testland"
    }
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {'msg': 'Agent created'}

        response = client.post('/agents', json=data)
        assert response.status_code == 201
        assert response.get_json() == {'msg': 'Agent created'}


def test_delete_agent(client):
    agent_id = 'agent-id'
    with patch('requests.delete') as mock_delete:
        mock_delete.return_value.status_code = 200
        response = client.delete(f'/agents/{agent_id}')
        assert response.status_code == 200
        assert response.get_json() == {'msg': 'Agent deleted successfully'}
