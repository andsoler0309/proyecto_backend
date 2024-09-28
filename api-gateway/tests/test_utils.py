from utils import generate_jwt, decode_jwt, blacklist_token, is_token_blacklisted
from config import Config
from unittest.mock import patch


def test_generate_jwt():
    token = generate_jwt('agent-id', 'session-id')
    assert token is not None


def test_decode_jwt():
    token = generate_jwt('agent-id', 'session-id')
    payload = decode_jwt(token)
    assert payload['agent_id'] == 'agent-id'
    assert payload['session_id'] == 'session-id'


def test_blacklist_token():
    with patch('models.db.session') as mock_session:
        blacklist_token('jti', 'token')
        mock_session.add.assert_called()
        mock_session.commit.assert_called()


def test_is_token_blacklisted():
    with patch('models.TokenBlacklist.query') as mock_query:
        mock_query.filter_by.return_value.first.return_value = True
        result = is_token_blacklisted('jti')
        assert result is True
