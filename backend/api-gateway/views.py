from flask import request, current_app
from flask_restful import Resource
from schemas import LoginSchema, SecurityAnswerSchema, VerificationSchema, AgentCreationSchema, IncidentCreationSchema
from config import Config
import requests
from openai import OpenAI
import uuid
import jwt
import datetime
import json
from functools import wraps
from utils import generate_jwt
from models import db, Verification, UserRole
from marshmallow import ValidationError
from auth import token_required, role_required

login_schema = LoginSchema()
security_answer_schema = SecurityAnswerSchema()
verification_schema = VerificationSchema()
agent_creation_schema = AgentCreationSchema()
incident_creation_schema = IncidentCreationSchema()


client = OpenAI(api_key=Config.OPENAI_API_KEY)


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

        email = validated_data['email']
        password = validated_data['password']

        current_app.logger.info(f"Login attempt for email: {email}")

        try:
            gestor_response = requests.post(
                f"{Config.GESTOR_AGENTES_BASE_URL}/agent/login",
                json={"email": email, "password": password},
                timeout=5
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Gestor-Agente: {e}")
            return {"msg": "Error communicating with Gestor-Agente"}, 503

        if gestor_response.status_code != 200:
            return {"msg": "Bad username or password"}, 401

        agent_data = gestor_response.json()

        agent_id = agent_data.get('id')

        if not agent_id:
            return {"msg": "Invalid agent data received"}, 500

        try:
            incidents_response = requests.get(
                f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents",
                params={"agent_id": agent_id},
                timeout=5
            )
            if incidents_response.status_code != 200:
                current_app.logger.error(f"Error fetching incidents: {incidents_response.text}")
                return {"msg": "Error fetching incidents"}, 500
            incidents = incidents_response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        # Generate security question using OpenAI
        try:
            prompt = (
                f"Create a security question for the following agent based on their personal data and incidents. be creative on the question\n\n"
                f"Agent Data: {agent_data}\n"
                f"Incidents: {incidents}\n\n"
                f"Security Question:"
            )

            openai_response = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="gpt-3.5-turbo",
            )

            security_question = openai_response.choices[0].message.content.strip()

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
            security_question=security_question
        )
        db.session.add(verification)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error storing verification data: {e}")
            return {"msg": "Internal server error"}, 500

        current_app.logger.info(f"Generated security question for agent_id: {agent_id}, verification_id: {verification_id}")

        return {
            "verification_id": verification_id,
            "security_question": security_question
        }, 200


class VerifySecurityAnswer(Resource):
    def post(self):
        data = request.get_json()
        try:
            validated_data = security_answer_schema.load(data)
        except ValidationError as err:
            return {"msg": "Invalid data", "errors": err.messages}, 400

        verification_id = validated_data['verification_id']
        user_answer = validated_data['answer']

        current_app.logger.info(f"Security answer verification attempt for verification_id: {verification_id}")

        # Retrieve verification details from the database
        verification = Verification.query.filter_by(verification_id=verification_id).first()
        if not verification:
            return {"msg": "Invalid or expired verification ID"}, 400

        agent_id = verification.agent_id
        security_question = verification.security_question

        # Fetch agent data from Gestor-Agente
        try:
            gestor_response = requests.get(
                f"{Config.GESTOR_AGENTES_BASE_URL}/agents/{agent_id}",
                timeout=5
            )
            if gestor_response.status_code != 200:
                current_app.logger.error(f"Agent not found: {agent_id}")
                return {"msg": "Agent not found"}, 404
            agent_data = gestor_response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Gestor-Agente: {e}")
            return {"msg": "Error communicating with Gestor-Agente"}, 503

        # Fetch incidents from Incidents Service
        try:
            incidents_response = requests.get(
                f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents",
                params={"agent_id": agent_id},
                timeout=5
            )
            if incidents_response.status_code != 200:
                current_app.logger.error(f"Error fetching incidents: {incidents_response.text}")
                return {"msg": "Error fetching incidents"}, 500
            incidents = incidents_response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        # Verify the answer using OpenAI
        try:
            prompt = (
                f"Based on the following agent data and incidents, determine if the user's answer is correct for the security question.\n\n"
                f"Security Question: {security_question}\n"
                f"Agent Data: {agent_data}\n"
                f"Incidents: {incidents}\n\n"
                f"User's Answer: {user_answer}\n\n"
                f"Is this answer correct? Respond with 'Yes' or 'No'."
            )

            openai_response = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="gpt-3.5-turbo",
            )

            verification_response = openai_response.choices[0].message.content.strip()
            print(verification_response)

            if verification_response not in ['Yes', 'No']:
                raise ValueError("Invalid verification response from OpenAI")
        except Exception as e:
            current_app.logger.error(f"Error verifying security answer with OpenAI: {e}")
            return {"msg": "Error verifying security answer"}, 500

        # Remove the verification entry from the database
        try:
            db.session.delete(verification)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting verification data: {e}")

        if verification_response == 'Yes':
            # Generate JWT token
            token = generate_jwt(agent_id)
            current_app.logger.info(f"Login successful for agent_id: {agent_id}, token issued.")
            return {"msg": "Login successful", "token": token}, 200
        else:
            current_app.logger.info(f"Incorrect security answer for verification_id: {verification_id}")
            return {"msg": "Incorrect security answer"}, 401


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
                timeout=5
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
                f"{Config.GESTOR_AGENTES_BASE_URL}/agents/{agent_id}",
                timeout=5
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Gestor-Agente: {e}")
            return {"msg": "Error communicating with Gestor-Agente"}, 503

        if gestor_response.status_code not in [200, 204]:
            return gestor_response.json(), gestor_response.status_code

        return {"msg": "Agent deleted successfully"}, 200


class CreateIncident(Resource):
    @token_required
    def post(self, current_agent):
        data = request.get_json()
        try:
            validated_data = incident_creation_schema.load(data)
        except ValidationError as err:
            return {"msg": "Invalid data", "errors": err.messages}, 400

        # Optionally, verify that the agent_id matches the current_agent's id
        if validated_data['agent_id'] != current_agent['id']:
            return {"msg": "Cannot create incident for another agent"}, 403

        # Forward the incident creation to Incidents service
        try:
            incidents_response = requests.post(
                f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents",
                json=validated_data,
                timeout=5
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        if incidents_response.status_code != 201:
            return incidents_response.json(), incidents_response.status_code

        return incidents_response.json(), 201


class DeleteIncident(Resource):
    @token_required
    def delete(self, current_agent, incident_id):
        # Optionally, verify that the incident belongs to the current_agent
        # This requires fetching the incident details
        try:
            incident_response = requests.get(
                f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents/{incident_id}",
                timeout=5
            )
            if incident_response.status_code != 200:
                return incident_response.json(), incident_response.status_code
            incident = incident_response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        if incident['agent_id'] != current_agent['id'] and current_agent['role'] != 'admin':
            return {"msg": "Unauthorized to delete this incident"}, 403

        # Forward the incident deletion to Incidents service
        try:
            delete_response = requests.delete(
                f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents/{incident_id}",
                timeout=5
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        if delete_response.status_code not in [200, 204]:
            return delete_response.json(), delete_response.status_code

        return {"msg": "Incident deleted successfully"}, 200


class ProtectedResource(Resource):
    @token_required
    def get(self, current_agent):
        print(current_agent)
        return {"msg": f"Hello, {current_agent.get('name')}"}, 200


class RoleProtectedResource(Resource):
    @token_required
    @role_required([UserRole.ADMIN])
    def get(self, current_agent):
        print(current_agent)
        return {"msg": "Hello, Admin"}, 200
