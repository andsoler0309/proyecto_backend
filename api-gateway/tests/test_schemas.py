from schemas import LoginSchema, SecurityAnswerSchema, AgentCreationSchema, IncidentCreationSchema
from marshmallow import ValidationError
import pytest


def test_login_schema():
    data = {'email': 'test@example.com', 'password': 'password'}
    result = LoginSchema().load(data)
    assert result['email'] == 'test@example.com'


def test_login_schema_invalid():
    data = {'email': 'invalid-email', 'password': 'password'}
    with pytest.raises(ValidationError):
        LoginSchema().load(data)


def test_agent_creation_schema():
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
    result = AgentCreationSchema().load(data)
    assert result['name'] == 'Test Agent'


def test_agent_creation_schema_invalid_role():
    data = {
        "name": "Test Agent",
        "email": "test.agent@example.com",
        "password": "password123",
        "role": "invalid-role",
        "identification": "123456789",
        "phone": "555-5555",
        "address": "123 Main St",
        "city": "Testville",
        "state": "Test State",
        "zip_code": "12345",
        "country": "Testland"
    }
    with pytest.raises(ValidationError):
        AgentCreationSchema().load(data)
