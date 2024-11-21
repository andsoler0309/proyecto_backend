import datetime

# from openai import OpenAI
import uuid

import requests
from flask import current_app, request
from flask_restful import Resource
from marshmallow import ValidationError

from auth import role_required, token_required
from config import Config
from models import (
    AgentIPAddress,
    IPAddressLoginAttempt,
    Session,
    UserRole,
    Verification,
    db,
)
from schemas import (
    AgentCreationSchema,
    LoginSchema,
    SecurityAnswerSchema,
    VerificationSchema,
)
from utils import (
    blacklist_token,
    decode_jwt,
    generate_jwt,
    increment_failed_attempts,
    is_new_ip,
    lock_agent_account,
    notify_admin,
    reset_failed_attempts,
)

login_schema = LoginSchema()
security_answer_schema = SecurityAnswerSchema()
verification_schema = VerificationSchema()
agent_creation_schema = AgentCreationSchema()


# client = OpenAI(api_key=Config.OPENAI_API_KEY)


class Ping(Resource):
    def get(self):
        return {"status": "alive"}, 200


class Login(Resource):
    def post(self):
        data = request.get_json()
        try:
            validated_data = login_schema.load(data)
        except ValidationError as err:
            return {"msg": "Invalid data", "errors": err.messages}, 400

        email = validated_data["email"]
        password = validated_data["password"]
        x_forwarded_for = request.headers.get("X-Forwarded-For", "")
        client_ip = (
            x_forwarded_for.split(",")[0].strip()
            if x_forwarded_for
            else request.remote_addr
        )
        user_agent = request.headers.get("User-Agent")

        current_app.logger.info(
            f"Login attempt for email: {email} from IP: {client_ip}, User-Agent: {user_agent}"
        )

        # Increment IP address login attempt count
        ip_attempt = IPAddressLoginAttempt.query.filter_by(ip_address=client_ip).first()
        if ip_attempt:
            ip_attempt.attempts += 1
            ip_attempt.last_attempt = datetime.datetime.utcnow()
        else:
            ip_attempt = IPAddressLoginAttempt(
                ip_address=client_ip,
                attempts=1,
                last_attempt=datetime.datetime.utcnow(),
            )
            db.session.add(ip_attempt)
        db.session.commit()

        current_app.logger.info(f"Login attempt for email: {email}")

        try:
            gestor_response = requests.post(
                f"{Config.GESTOR_AGENTES_BASE_URL}/agent/login",
                json={"email": email, "password": password},
                timeout=900,
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Gestor-Agente: {e}")
            return {"msg": "Error communicating with Gestor-Agente"}, 503

        if gestor_response.status_code == 403:
            return {
                "msg": "Your account is locked due to multiple failed attempts. Please contact an administrator."
            }, 403

        if gestor_response.status_code != 200:
            return {"msg": "Bad username or password"}, 401

        agent_data = gestor_response.json()
        agent_id = agent_data.get("id")

        if not agent_id:
            return {"msg": "Invalid agent data received"}, 500

        if agent_data.get("is_locked"):
            return {
                "msg": "Your account is locked due to multiple failed attempts. Please contact an administrator."
            }, 403

        known_ip = AgentIPAddress.query.filter_by(
            agent_id=agent_id, ip_address=client_ip
        ).first()
        if known_ip:
            # Update last used and increment login count
            known_ip.last_used = datetime.datetime.utcnow()
            known_ip.login_count += 1
            db.session.commit()
            is_suspicious = False

        if is_new_ip(agent_id, client_ip):
            # New IP address for this agent
            new_ip = AgentIPAddress(
                agent_id=agent_id,
                ip_address=client_ip,
                first_used=datetime.datetime.utcnow(),
                last_used=datetime.datetime.utcnow(),
                login_count=1,
            )
            db.session.add(new_ip)
            db.session.commit()
            is_suspicious = True
            current_app.logger.warning(
                f"Suspicious login attempt for agent_id: {agent_id} from new IP: {client_ip}"
            )

            notify_admin(
                subject="Suspicious Login Attempt",
                message=f"Agent {agent_id} attempted to login from a new IP address: {client_ip}",
            )

        try:
            incidents_response = requests.get(
                f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents/agent/{agent_id}",
                timeout=900,
            )
            if incidents_response.status_code != 200:
                current_app.logger.error(
                    f"Error fetching incidents: {incidents_response.text}"
                )
                return {"msg": "Error fetching incidents"}, 500
            incidents = incidents_response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        # Generate security question using OpenAI
        agent_data.pop("is_locked", None)
        try:
            # prompt = (
            #     f"Crea una pregunta de seguridad para verificar que si sea el agente, esta pregunta hazla basada en la informacion que te paso en este mensaje, solo dame la pregunta de seguridad sin nada mas:\n\n"
            #     f"Data agente: {agent_data}\n"
            #     f"Incidentes: {incidents}\n\n"
            #     f"Pregunta de seguridad:"
            # )

            # openai_response = client.chat.completions.create(
            #     messages=[
            #         {
            #             "role": "user",
            #             "content": prompt,
            #         }
            #     ],
            #     model="gpt-4o",
            # )

            # security_question = openai_response.choices[0].message.content.strip()
            security_question = "cual es el nomrbe del proyecto? repsuesta abcall"

            if not security_question:
                raise ValueError("Empty security question generated")
        except Exception as e:
            current_app.logger.error(f"Error generating security question: {e}")
            return {"msg": "Error generating security question"}, 500

        # Store verification details in the database with an expiration time (e.g., 10 minutes)
        verification_id = str(uuid.uuid4())
        verification = Verification(
            verification_id=verification_id,
            agent_id=agent_id,
            security_question=security_question,
        )
        db.session.add(verification)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error storing verification data: {e}")
            return {"msg": "Internal server error"}, 500

        current_app.logger.info(
            f"Generated security question for agent_id: {agent_id}, verification_id: {verification_id}"
        )

        return {
            "verification_id": verification_id,
            "security_question": security_question,
        }, 200


class VerifySecurityAnswer(Resource):
    def post(self):
        data = request.get_json()
        try:
            validated_data = security_answer_schema.load(data)
        except ValidationError as err:
            return {"msg": "Invalid data", "errors": err.messages}, 400

        verification_id = validated_data["verification_id"]
        user_answer = validated_data["answer"]

        current_app.logger.info(
            f"Security answer verification attempt for verification_id: {verification_id}"
        )

        # Retrieve verification details from the database
        verification = Verification.query.filter_by(
            verification_id=verification_id
        ).first()
        if not verification:
            return {"msg": "Invalid or expired verification ID"}, 400

        agent_id = verification.agent_id
        security_question = verification.security_question

        # Fetch agent data from Gestor-Agente
        try:
            gestor_response = requests.get(
                f"{Config.GESTOR_AGENTES_BASE_URL}/agents/{agent_id}", timeout=900
            )
            if gestor_response.status_code != 200:
                current_app.logger.error(f"Agent not found: {agent_id}")
                return {"msg": "Agent not found"}, 404
            agent_data = gestor_response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Gestor-Agente: {e}")
            return {"msg": "Error communicating with Gestor-Agente"}, 503

        # Check if agent account is locked
        if agent_data.get("is_locked"):
            return {
                "msg": "Your account is locked due to multiple failed attempts. Please contact an administrator."
            }, 403

        # Fetch incidents from Incidents Service
        try:
            incidents_response = requests.get(
                f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents/agent/{agent_id}",
                timeout=900,
            )
            if incidents_response.status_code != 200:
                current_app.logger.error(
                    f"Error fetching incidents: {incidents_response.text}"
                )
                return {"msg": "Error fetching incidents"}, 500
            incidents = incidents_response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        # Verify the answer using OpenAI
        try:
            # prompt = (
            #     f"Based on the following agent data and incidents, determine if the user's answer is correct for the security question, think like a human responding so ignore some situations like case sensitive, etc.\n\n"
            #     f"Security Question: {security_question}\n"
            #     f"Agent Data: {agent_data}\n"
            #     f"Incidents: {incidents}\n\n"
            #     f"User's Answer: {user_answer}\n\n"
            #     f"Is this answer correct? Respond only with 'Yes' or 'No'."
            # )

            # openai_response = client.chat.completions.create(
            #     messages=[
            #         {
            #             "role": "user",
            #             "content": prompt,
            #         }
            #     ],
            #     model="gpt-3.5-turbo",
            # )

            # verification_response = openai_response.choices[0].message.content.strip()
            verification_response = "Yes"

            if verification_response not in ["Yes", "No"]:
                raise ValueError("Invalid verification response from OpenAI")
        except Exception as e:
            current_app.logger.error(
                f"Error verifying security answer with OpenAI: {e}"
            )
            return {"msg": "Error verifying security answer"}, 500

        # Remove the verification entry from the database
        try:
            db.session.delete(verification)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting verification data: {e}")

        if verification_response == "Yes":
            reset_failed_attempts(agent_id)

            # Create a new session
            session_id = str(uuid.uuid4())
            new_session = Session(
                session_id=session_id,
                agent_id=agent_id,
                last_activity=datetime.datetime.utcnow(),
                ip_address=request.remote_addr,
                user_agent=request.headers.get("User-Agent"),
            )
            db.session.add(new_session)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error creating session: {e}")
                return {"msg": "Internal server error"}, 500

            # Generate JWT token including session_id
            token = generate_jwt(agent_id, session_id)
            current_app.logger.info(
                f"Login successful for agent_id: {agent_id}, token issued."
            )

            return {
                "msg": "Login successful",
                "token": token,
                "agent_id": agent_id,
            }, 200
        else:
            # Increment failed attempts
            attempts = increment_failed_attempts(agent_id)
            current_app.logger.info(
                f"Incorrect security answer for verification_id: {verification_id}. Attempts: {attempts}"
            )
            if attempts >= Config.MAX_FAILED_ATTEMPTS:
                # Lock the agent account
                lock_agent_account(agent_id)
                notify_admin(
                    subject="Agent Account Locked",
                    message=f"Agent {agent_id} has been locked due to multiple failed security answers.",
                )
                return {
                    "msg": "Your account has been locked due to multiple failed attempts. Please contact an administrator."
                }, 403

            return {"msg": "Incorrect security answer"}, 401


class Logout(Resource):
    @token_required
    def post(self, current_agent):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
        if not token:
            return {"msg": "Token is missing"}, 401

        try:
            payload = decode_jwt(token)
            if not payload:
                return {"msg": "Invalid or expired token"}, 401
            jti = payload.get("jti")
            session_id = payload.get("session_id")
            if not jti:
                return {"msg": "Invalid token"}, 401

            blacklist_token(jti, token)
            current_app.logger.info(f"Token {jti} has been blacklisted.")

            # Delete the session
            session = Session.query.filter_by(session_id=session_id).first()
            if session:
                db.session.delete(session)
                db.session.commit()
                current_app.logger.info(f"Session {session_id} has been terminated.")
            return {"msg": "Successfully logged out"}, 200
        except Exception as e:
            current_app.logger.error(f"Error during logout: {e}")
            return {"msg": "Error during logout"}, 500


class CreateAgent(Resource):
    def post(self):
        data = request.get_json()
        try:
            validated_data = agent_creation_schema.load(data)
        except ValidationError as err:
            return {"msg": "Invalid data", "errors": err.messages}, 400

        # Forward the agent creation to Gestor-Agente service
        try:
            gestor_response = requests.post(
                f"{Config.GESTOR_AGENTES_BASE_URL}/agents/register",
                json=validated_data,
                timeout=900,
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Gestor-Agente: {e}")
            return {"msg": "Error communicating with Gestor-Agente"}, 503

        if gestor_response.status_code != 201:
            return gestor_response.json(), gestor_response.status_code

        return gestor_response.json(), 201


class DeleteAgent(Resource):
    def delete(self, agent_id):
        # Forward the agent deletion to Gestor-Agente service
        try:
            gestor_response = requests.delete(
                f"{Config.GESTOR_AGENTES_BASE_URL}/agents/{agent_id}", timeout=900
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Gestor-Agente: {e}")
            return {"msg": "Error communicating with Gestor-Agente"}, 503

        if gestor_response.status_code not in [200, 204]:
            return gestor_response.json(), gestor_response.status_code

        return {"msg": "Agent deleted successfully"}, 200


class AdminUnlockAgent(Resource):
    @role_required([UserRole.ADMIN.name])
    def post(self, current_agent, agent_id):
        # Unlock the agent account via Gestor-Agente
        try:
            response = requests.post(
                f"{Config.GESTOR_AGENTES_BASE_URL}/agents/{agent_id}/unlock",
                timeout=900,
            )
            if response.status_code == 200:
                # Reset failed attempts
                reset_failed_attempts(agent_id)
                return {"msg": f"Agent {agent_id} has been unlocked"}, 200
            else:
                return {"msg": "Failed to unlock agent"}, response.status_code
        except Exception as e:
            current_app.logger.error(f"Error communicating with Gestor-Agente: {e}")
            return {"msg": "Error communicating with Gestor-Agente"}, 503


class AdminResetAgent(Resource):
    @role_required([UserRole.ADMIN.name])
    def post(self, current_agent, agent_id):
        # Reset agent data via Gestor-Agente
        try:
            response = requests.post(
                f"{Config.GESTOR_AGENTES_BASE_URL}/agents/{agent_id}/reset", timeout=900
            )
            if response.status_code == 200:
                return {"msg": f"Agent {agent_id} has been reset"}, 200
            else:
                return {"msg": "Failed to reset agent"}, response.status_code
        except Exception as e:
            current_app.logger.error(f"Error communicating with Gestor-Agente: {e}")
            return {"msg": "Error communicating with Gestor-Agente"}, 503


class AgentDetail(Resource):
    def get(self, agent_id):
        # Retrieve agent details from Gestor-Agente
        try:
            response = requests.get(
                f"{Config.GESTOR_AGENTES_BASE_URL}/agents/{agent_id}", timeout=900
            )
            if response.status_code == 200:
                return response.json(), 200
            else:
                return {"msg": "Agent not found"}, 404
        except Exception as e:
            current_app.logger.error(f"Error communicating with Gestor-Agente: {e}")
            return {"msg": "Error communicating with Gestor-Agente"}, 503