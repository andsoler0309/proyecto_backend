# tests/test_resources.py

import pytest
from unittest.mock import MagicMock, patch
from models import Agent, UserRole


def test_ping(client):
    response = client.get('/gestor-agentes/ping')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'alive'}


def test_agent_registration_success(client, mock_models):
    mock_models.query.filter_by.return_value.first.side_effect = [MagicMock(), None]

    data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "password123",
        "role": "agent",
        "identification": "987654321",
        "phone": "555-4321",
        "address": "456 Main St",
        "city": "Othertown",
        "state": "Otherstate",
        "zip_code": "54321",
        "country": "USA"
    }

    response = client.post('/agents/register', json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['msg'] == 'Email already exists'


def test_agent_registration_missing_field(client):
    data = {
        "email": "john@example.com",
        "password": "password123",
        "role": "agent",
        # Falta el campo "name"
        "identification": "123456789",
        "phone": "555-1234",
        "address": "123 Main St",
        "city": "Anytown",
        "state": "Anystate",
        "zip_code": "12345",
        "country": "USA"
    }

    response = client.post('/agents/register', json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert "Missing required field" in json_data['msg']


def test_agent_registration_duplicate_email(client, mock_models):
    # Simular que el agente con el email ya existe
    mock_models.query.filter_by.return_value.first.side_effect = [MagicMock(), None]

    data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "password123",
        "role": "agent",
        "identification": "987654321",
        "phone": "555-4321",
        "address": "456 Main St",
        "city": "Othertown",
        "state": "Otherstate",
        "zip_code": "54321",
        "country": "USA"
    }

    response = client.post('/agents/register', json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['msg'] == 'Email already exists'


def test_agent_login_success(client):
    with patch('views.Agent.query') as MockQuery:
        # Create a real Agent instance
        agent = Agent(
            id='agent123',
            name='John Doe',
            email='login@example.com',
            role=UserRole.AGENT,
            identification='ID123',
            phone='555-1234',
            address='123 Main St',
            city='Anytown',
            state='Anystate',
            zip_code='12345',
            country='USA',
            is_locked=False,
        )
        agent.set_password('password123')  # Set the password

        # Mock methods
        agent.check_password = lambda password: password == 'password123'

        # Mock the query to return the real agent
        MockQuery.filter_by.return_value.first.return_value = agent

        # Prepare the login data
        login_data = {
            "email": "login@example.com",
            "password": "password123"
        }

        # Perform the test
        response = client.post('/agent/login', json=login_data)

        # Assert the response
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['email'] == login_data['email']
        assert json_data['name'] == 'John Doe'


def test_agent_login_wrong_password(client, mock_views):
    # Simular que el agente existe y la contraseña es incorrecta
    mock_agent = MagicMock()
    mock_agent.check_password.return_value = False
    mock_agent.is_locked = False
    mock_views.query.filter_by.return_value.first.return_value = mock_agent

    login_data = {
        "email": "login@example.com",
        "password": "wrongpassword"
    }

    response = client.post('/agent/login', json=login_data)
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['msg'] == 'Bad username or password'


def test_agent_login_locked(client, mock_models):
    with patch('views.Agent.query') as MockQuery:
        # Create a real Agent instance
        agent = Agent(
            id='agent123',
            name='John Doe',
            email='login@example.com',
            role=UserRole.AGENT,
            identification='ID123',
            phone='555-1234',
            address='123 Main St',
            city='Anytown',
            state='Anystate',
            zip_code='12345',
            country='USA',
            is_locked=True,  # Agent is locked
        )
        agent.set_password('password123')  # Set the password

        # Mock methods
        agent.check_password = lambda password: password == 'password123'

        # Mock the query to return the real agent
        MockQuery.filter_by.return_value.first.return_value = agent

        # Prepare the login data
        login_data = {
            "email": "login@example.com",
            "password": "password123"
        }

        # Perform the test
        response = client.post('/agent/login', json=login_data)

        # Assert the response
        assert response.status_code == 403
        json_data = response.get_json()
        assert json_data['msg'] == 'Your account is locked. Please contact an administrator.'


def test_agent_detail(client):
    with patch('views.Agent') as MockAgent:
        # Create a real Agent instance
        agent = Agent(
            id='agent123',
            name='Detail User',
            email='detail@example.com',
            role=UserRole.AGENT,
            identification='555444333',
            phone='555-5555',
            address='Detail St',
            city='Detail City',
            state='Detail State',
            zip_code='55555',
            country='USA',
            is_locked=False,
        )
        # Mock the query.get to return our agent
        MockAgent.query.get.return_value = agent

        # Perform the request
        response = client.get('/agents/agent123')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['email'] == 'detail@example.com'
        assert json_data['name'] == 'Detail User'


def test_agent_lock(client):
    with patch('views.Agent') as MockAgent, patch('views.db.session') as mock_session:
        # Create an agent that is not locked
        agent = Agent(
            id='agent123',
            name='Lock User',
            email='lock@example.com',
            role=UserRole.AGENT,
            identification='666777888',
            phone='555-6666',
            address='Lock St',
            city='Lock City',
            state='Lock State',
            zip_code='66666',
            country='USA',
            is_locked=False,  # Initially not locked
        )

        # Mock the query.get to return our agent
        MockAgent.query.get.return_value = agent

        # Mock db.session.commit() to avoid database operations
        mock_session.commit.return_value = None

        # Perform the request
        response = client.post('/agents/agent123/lock')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['msg'] == f'Agent agent123 has been locked'
        assert agent.is_locked is True


def test_agent_unlock(client):
    with patch('views.Agent') as MockAgent, patch('views.db.session') as mock_session:
        # Create an agent that is locked
        agent = Agent(
            id='agent123',
            name='Unlock User',
            email='unlock@example.com',
            role=UserRole.AGENT,
            identification='777888999',
            phone='555-7777',
            address='Unlock St',
            city='Unlock City',
            state='Unlock State',
            zip_code='77777',
            country='USA',
            is_locked=True,  # Initially locked
        )

        # Mock the query.get to return our agent
        MockAgent.query.get.return_value = agent

        # Mock db.session.commit() to avoid database operations
        mock_session.commit.return_value = None

        # Perform the request
        response = client.post('/agents/agent123/unlock')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['msg'] == f'Agent agent123 has been unlocked'
        assert agent.is_locked is False


def test_agent_reset(client):
    with patch('views.Agent') as MockAgent, patch('views.db.session') as mock_session:
        # Create a mock agent
        agent = MagicMock()
        agent.id = 'agent123'

        # Mock the query.get to return our mock agent
        MockAgent.query.get.return_value = agent

        # Mock db.session.commit() to avoid database operations
        mock_session.commit.return_value = None

        # Perform the request
        response = client.post('/agents/agent123/reset')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['msg'] == f'Agent agent123 has been reset'

        # Assert that set_password was called with '1234567890'
        agent.set_password.assert_called_with('1234567890')



def test_admin_list(client):
    with patch('views.Agent') as MockAgent:
        # Create a real admin agent
        admin_agent = Agent(
            id='admin123',
            name='Admin User',
            email='admin@example.com',
            role=UserRole.ADMIN,
            identification='000111222',
            phone='555-0000',
            address='Admin St',
            city='Admin City',
            state='Admin State',
            zip_code='00000',
            country='USA',
            is_locked=False,
        )

        # Mock the query to return a list with our admin agent
        MockAgent.query.filter_by.return_value.all.return_value = [admin_agent]

        # Perform the request
        response = client.get('/agents/admins')
        assert response.status_code == 200
        json_data = response.get_json()
        assert isinstance(json_data, list)
        assert len(json_data) >= 1
        admin_emails = [admin['email'] for admin in json_data]
        assert 'admin@example.com' in admin_emails
