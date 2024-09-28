import datetime
from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import UserRole, Session, db
import jwt
from config import Config
import requests

from utils import decode_jwt, is_token_blacklisted


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
            payload = decode_jwt(token)
            if not payload:
                return {"msg": "Invalid or expired token"}, 401
            jti = payload.get('jti')
            if is_token_blacklisted(jti):
                return {"msg": "Token has been revoked"}, 401
            agent_id = payload['agent_id']
            session_id = payload.get('session_id')

            session = Session.query.filter_by(session_id=session_id, agent_id=agent_id).first()
            if not session:
                return {"msg": "Invalid session or session expired"}, 401

            # Check inactivity timeout
            inactivity_limit = datetime.timedelta(minutes=Config.SESSION_INACTIVITY_LIMIT)
            now = datetime.datetime.utcnow()
            if now - session.last_activity > inactivity_limit:
                # Invalidate the session
                db.session.delete(session)
                db.session.commit()
                return {"msg": "Session has expired due to inactivity"}, 401

            # Update last activity time
            session.last_activity = now
            db.session.commit()

            # Verify agent existence via Gestor-Agente
            response = requests.get(f"{Config.GESTOR_AGENTES_BASE_URL}/agents/{agent_id}", timeout=5)
            if response.status_code != 200:
                return {"msg": "Agent not found"}, 401
            current_agent = response.json()
        except Exception as e:
            return {"msg": "Token verification failed"}, 401

        return f(args[0], current_agent, *args[1:], **kwargs)
    return decorated


def role_required(required_roles):
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
                payload = decode_jwt(token)
                agent_id = payload['agent_id']

                # Verify agent existence via Gestor-Agente
                response = requests.get(f"{Config.GESTOR_AGENTES_BASE_URL}/agents/{agent_id}", timeout=5)
                if response.status_code != 200:
                    return {"msg": "Agent not found"}, 401

                current_agent = response.json()
                agent_role_str = current_agent.get('role')
                if not agent_role_str:
                    return {"msg": "Role information missing"}, 401

                # Check if the agent has the required role
                if agent_role_str not in required_roles:
                    return {"msg": f"Access denied for role: {agent_role_str}"}, 403

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
