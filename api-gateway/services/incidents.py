import datetime

import requests
from flask import current_app, request
from flask_restful import Resource
from marshmallow import ValidationError

from auth import token_required, role_required
from config import Config
from schemas import IncidentCreationSchema, IncidentUpdateSchema
from models import UserRole

incident_creation_schema = IncidentCreationSchema()
incident_update_schema = IncidentUpdateSchema()


class CreateIncident(Resource):
    @token_required
    def post(self, current_agent):
        data = request.get_json()
        try:
            validated_data = incident_creation_schema.load(data)
        except ValidationError as err:
            return {"msg": "Invalid data", "errors": err.messages}, 400

        if validated_data["agent_id"] != current_agent["id"]:
            return {"msg": "Cannot create incident for another agent"}, 403

        for key, value in validated_data.items():
            if isinstance(value, datetime.date):
                validated_data[key] = value.isoformat()

        validated_data["registration_medium"] = validated_data[
            "registration_medium"
        ].upper()

        # Forward the incident creation to Incidents service
        try:
            incidents_response = requests.post(
                f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents",
                json=validated_data,
                timeout=5,
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        if incidents_response.status_code != 201:
            return incidents_response.json(), incidents_response.status_code

        return incidents_response.json(), 201


class DeleteIncident(Resource):
    @role_required([UserRole.ADMIN.name])
    def delete(self, current_agent, incident_id):
        try:
            incident_response = requests.get(
                f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents/{incident_id}",
                timeout=5,
            )
            if incident_response.status_code != 200:
                return incident_response.json(), incident_response.status_code
            incident = incident_response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        # Forward the incident deletion to Incidents service
        try:
            delete_response = requests.delete(
                f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents/{incident_id}",
                timeout=5,
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        if delete_response.status_code not in [200, 204]:
            return delete_response.json(), delete_response.status_code

        return {"msg": "Incident deleted successfully"}, 200


class UpdateIncident(Resource):
    @token_required
    def put(self, current_agent, incident_id):
        data = request.get_json()
        try:
            validated_data = incident_update_schema.load(data)
        except ValidationError as err:
            return {"msg": "Invalid data", "errors": err.messages}, 400

        try:
            incident_response = requests.get(
                f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents/{incident_id}",
                timeout=5,
            )
            if incident_response.status_code != 200:
                return incident_response.json(), incident_response.status_code
            incident = incident_response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        for key, value in validated_data.items():
            if isinstance(value, datetime.date):
                validated_data[key] = value.isoformat()

        validated_data["registration_medium"] = validated_data[
            "registration_medium"
        ].upper()

        # Forward the incident update to Incidents service
        try:
            update_response = requests.put(
                f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents/{incident_id}",
                json=validated_data,
                timeout=5,
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        if update_response.status_code != 200:
            return update_response.json(), update_response.status_code

        return update_response.json(), 200


class GetIncidentDetail(Resource):
    @token_required
    def get(self, current_agent, incident_id):
        try:
            incident_response = requests.get(
                f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents/{incident_id}",
                timeout=5,
            )
            if incident_response.status_code != 200:
                return incident_response.json(), incident_response.status_code
            incident = incident_response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        if (
            incident["agent_id_creation"] != current_agent["id"]
            or incident["agent_id_last_update"] != current_agent["id"]
        ) and current_agent["role"] != "admin":
            return {"msg": "Unauthorized to view this incident"}, 403

        return incident, 200


class GetIncidentsByUser(Resource):
    @token_required
    def get(self, current_agent, user_id):
        try:
            incidents_response = requests.get(
                f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents/user/{user_id}",
                timeout=5,
            )
            if incidents_response.status_code != 200:
                return incidents_response.json(), incidents_response.status_code
            incidents = incidents_response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        return incidents, 200


class GetIncidentsByAgent(Resource):
    @token_required
    def get(self, current_agent):
        agent_id = current_agent["id"]

        try:
            incidents_response = requests.get(
                f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents/agent/{agent_id}",
                timeout=5,
            )
            if incidents_response.status_code != 200:
                return incidents_response.json(), incidents_response.status_code
            incidents = incidents_response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        return incidents, 200


class GetIncidentsByClient(Resource):
    @token_required
    def get(self, current_agent, client_id):
        try:
            incidents_response = requests.get(
                f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents/client/{client_id}",
                timeout=5,
            )
            if incidents_response.status_code != 200:
                return incidents_response.json(), incidents_response.status_code
            incidents = incidents_response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        return incidents, 200