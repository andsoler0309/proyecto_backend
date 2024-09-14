from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import UserRole
import jwt
from config import Config
import requests


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        if not token:
            return {"msg": "Token is missing"}, 401

        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
            print(payload)
            agent_id = payload['agent_id']

            # Verify agent existence via Gestor-Agente
            response = requests.get(f"{Config.GESTOR_AGENTES_BASE_URL}/agents/{agent_id}", timeout=5)
            if response.status_code != 200:
                return {"msg": "Agent not found"}, 401

            print(response.json())
            current_agent = response.json()
        except jwt.ExpiredSignatureError:
            return {"msg": "Token has expired"}, 401
        except jwt.InvalidTokenError:
            return {"msg": "Invalid token"}, 401
        except Exception as e:
            return {"msg": "Token verification failed"}, 401

        return f(args[0], current_agent, *args[1:], **kwargs)
    return decorated


def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                parts = auth_header.split()
                if len(parts) == 2 and parts[0].lower() == 'bearer':
                    token = parts[1]
            if not token:
                return {"msg": "Token is missing"}, 401

            try:
                payload = jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
                agent_id = payload['agent_id']

                # Verify agent existence via Gestor-Agente
                response = requests.get(f"{Config.GESTOR_AGENTES_BASE_URL}/agents/{agent_id}", timeout=5)
                if response.status_code != 200:
                    return {"msg": "Agent not found"}, 401

                current_agent = response.json()

                agent_role = current_agent.get('role', None)  # Check for role in the payload

                # Check if the agent has the required role
                if agent_role != required_role:
                    return {"msg": f"Access denied for role: {agent_role}"}, 403

            except jwt.ExpiredSignatureError:
                return {"msg": "Token has expired"}, 401
            except jwt.InvalidTokenError:
                return {"msg": "Invalid token"}, 401
            except Exception as e:
                return {"msg": "Token verification failed"}, 401

            # Pass 'self' (args[0]) and 'current_agent' to the original method
            return f(args[0], current_agent, *args[1:], **kwargs)
        return decorated
    return decorator
