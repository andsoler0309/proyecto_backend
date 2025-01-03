from flask import request
from flask_restful import Resource
from models import db, Incident
from schemas import IncidentSchema, IncidentUpdateSchema
from sqlalchemy.exc import IntegrityError
from models import RegistrationMediumEnum, StatusEnum
import os
import requests
import firebase_admin
from firebase_admin import messaging, credentials

incident_schema = IncidentSchema()
incidents_schema = IncidentSchema(many=True)

incident_update_schema = IncidentUpdateSchema()

SERVICIO_IA_BASE_URL = os.environ.get("SERVICIO_IA_BASE_URL", "http://localhost:5001")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
firebase_admin.initialize_app(cred)


class IncidentList(Resource):
    def post(self):
        data = request.get_json()
        try:
            incident_data = incident_schema.load(data)
        except Exception as e:
            return {"msg": "Invalid data", "error": str(e)}, 400

        registration_medium = incident_data["registration_medium"]
        try:
            registration_medium_enum = RegistrationMediumEnum(registration_medium)
        except ValueError:
            return {"msg": "Invalid registration medium"}, 400

        if registration_medium_enum is not RegistrationMediumEnum.CHAT:
            if "agent_id" not in incident_data:
                return {"msg": "Agent ID is required"}, 400

        incident = Incident(
            description=incident_data["description"],
            date=incident_data["date"],
            registration_medium=registration_medium_enum,
            user_id=incident_data["user_id"],
            client_id=incident_data["client_id"],
        )

        if "agent_id" in incident_data:
            incident.agent_id_creation = incident_data["agent_id"]
            incident.agent_id_last_update = incident_data["agent_id"]

        db.session.add(incident)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"msg": "Error creating incident"}, 500

        return incident_schema.dump(incident), 201


class GetIncidentsByAgentId(Resource):
    def get(self, agent_id):
        incidents = Incident.query.filter_by(agent_id_creation=agent_id).all()
        return incidents_schema.dump(incidents), 200


class IncidentDetail(Resource):
    def get(self, incident_id):
        incident = Incident.query.get(incident_id)
        if not incident:
            return {"msg": "Incident not found"}, 404
        return incident_schema.dump(incident), 200

    def delete(self, incident_id):
        incident = Incident.query.get(incident_id)
        if not incident:
            return {"msg": "Incident not found"}, 404
        db.session.delete(incident)
        db.session.commit()
        return {"msg": "Incident deleted"}, 200

    def put(self, incident_id):
        incident = Incident.query.get(incident_id)
        if not incident:
            return {"msg": "Incident not found"}, 404

        data = request.get_json()
        try:
            incident_data = incident_update_schema.load(data)
        except Exception as e:
            return {"msg": "Invalid data", "error": str(e)}, 400

        registration_medium = incident_data["registration_medium"]
        try:
            registration_medium_enum = RegistrationMediumEnum(registration_medium)
        except ValueError:
            return {"msg": "Invalid registration medium"}, 400

        status = incident_data["status"]
        try:
            status_enum = StatusEnum(status)
        except ValueError:
            return {"msg": "Invalid status"}, 400

        incident.description = incident_data["description"]
        incident.date = incident_data["date"]
        incident.registration_medium = registration_medium_enum
        incident.user_id = incident_data["user_id"]
        incident.agent_id_last_update = incident_data["agent_id"]
        incident.status = status_enum

        db.session.add(incident)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"msg": "Error updating incident"}, 500

        # The topic name can be optionally prefixed with "/topics/".
        topic = incident_id

        notification = messaging.Notification(
            title="ABCall",
            body="Hay cambios en el incidente"
        )
        # See documentation on defining a message payload.
        message = messaging.Message(
            data={
                'incident_id': incident_id,
            },
            notification=notification,  
            topic=topic,
        )

        # Send a message to the devices subscribed to the provided topic.
        response = messaging.send(message)
        # Response is a message ID string.
        print('Successfully sent message:', response)

        return incident_schema.dump(incident), 200


class GetIncidentsByUser(Resource):
    def get(self, user_id):
        incidents = Incident.query.filter_by(user_id=user_id).all()
        return incidents_schema.dump(incidents), 200


class GetIncidentsByClient(Resource):
    def get(self, client_id):
        incidents = Incident.query.filter_by(client_id=client_id).all()
        return incidents_schema.dump(incidents), 200


class GetIncidentPossibleSolution(Resource):
    def get(self, incident_id):
        incident = Incident.query.get(incident_id)
        if not incident:
            return {"msg": "Incident not found"}, 404

        incident_data = incident_schema.dump(incident)
        incident_description = incident_data["description"]

        try:
            response = requests.get(
                f"{SERVICIO_IA_BASE_URL}/incident/{incident_id}",
                timeout=900,
            )
        except requests.exceptions.RequestException as e:
            return {"msg": "Error communicating with IA Service"}, 503

        return response.json(), response.status_code


class Ping(Resource):
    def get(self):
        return {"status": "alive"}, 200
