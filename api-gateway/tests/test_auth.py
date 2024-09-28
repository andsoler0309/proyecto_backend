from flask import Flask
from flask.views import MethodView
from unittest.mock import patch
import datetime
from auth import token_required, role_required
from models import UserRole


def test_token_required(app):
    app = Flask(__name__)

    class ProtectedView(MethodView):
        @token_required
        def get(self, current_agent):
            return {'msg': 'Access granted'}

    app.add_url_rule('/protected', view_func=ProtectedView.as_view('protected'))
    client = app.test_client()

    # Test without token
    response = client.get('/protected')
    assert response.status_code == 401
    assert response.get_json()['msg'] == 'Token is missing'

    # Test with invalid token
    headers = {'Authorization': 'Bearer invalid-token'}
    response = client.get('/protected', headers=headers)
    assert response.status_code == 401

    # Test with valid token
    valid_token = 'valid-token'
    with patch('auth.decode_jwt') as mock_decode_jwt, \
            patch('auth.is_token_blacklisted') as mock_blacklisted, \
            patch('requests.get') as mock_get, \
            patch('models.Session.query') as mock_session_query:
        mock_decode_jwt.return_value = {
            'agent_id': 'agent-id',
            'jti': 'jti',
            'session_id': 'session-id'
        }
        mock_blacklisted.return_value = False
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'id': 'agent-id', 'role': 'agent'}
        mock_session = mock_session_query.filter_by.return_value.first.return_value
        mock_session.last_activity = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)

        headers = {'Authorization': f'Bearer {valid_token}'}
        response = client.get('/protected', headers=headers)
        assert response.status_code == 200
        assert response.get_json()['msg'] == 'Access granted'


def test_role_required():
    app = Flask(__name__)

    class ProtectedView(MethodView):
        @role_required([UserRole.ADMIN.name])
        def get(self, current_agent):
            return {'msg': 'Admin access granted'}

    app.add_url_rule('/admin-only', view_func=ProtectedView.as_view('admin-only'))
    client = app.test_client()

    # Test without token
    response = client.get('/admin-only')
    assert response.status_code == 401
    assert response.get_json()['msg'] == 'Token is missing'

    with patch('auth.decode_jwt') as mock_decode_jwt, \
            patch('auth.is_token_blacklisted') as mock_blacklisted, \
            patch('requests.get') as mock_get, \
            patch('models.Session.query') as mock_session_query:
        # Mock decode_jwt to return a valid payload
        mock_decode_jwt.return_value = {
            'agent_id': 'agent-id',
            'jti': 'jti',
            'session_id': 'session-id'
        }

        # Mock is_token_blacklisted to return False
        mock_blacklisted.return_value = False

        # Mock the external request to verify the agent
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'id': 'agent-id', 'role': 'agent'}

        # Mock the session query
        mock_session = mock_session_query.filter_by.return_value.first.return_value
        mock_session.last_activity = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)

        headers = {'Authorization': 'Bearer valid-token'}
        response = client.get('/admin-only', headers=headers)
        assert response.status_code == 403
        assert 'Access denied' in response.get_json()['msg']

    # Test with admin role
    with patch('auth.decode_jwt') as mock_decode_jwt, \
            patch('auth.is_token_blacklisted') as mock_blacklisted, \
            patch('requests.get') as mock_get, \
            patch('models.Session.query') as mock_session_query:
        # Mock decode_jwt to return a valid payload
        mock_decode_jwt.return_value = {
            'agent_id': 'agent-id',
            'jti': 'jti',
            'session_id': 'session-id'
        }

        # Mock is_token_blacklisted to return False
        mock_blacklisted.return_value = False

        # Mock the external request to verify the agent
        mock_get.return_value.status_code = 200
        role_str = UserRole.ADMIN.name
        mock_get.return_value.json.return_value = {'id': 'agent-id', 'role': role_str}

        # Mock the session query
        mock_session = mock_session_query.filter_by.return_value.first.return_value
        mock_session.last_activity = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)

        headers = {'Authorization': 'Bearer valid-token'}
        response = client.get('/admin-only', headers=headers)
        assert response.status_code == 200
        assert response.get_json()['msg'] == 'Admin access granted'
