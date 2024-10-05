from flask import request
from flask_restful import Resource
from models import db, Incident
from schemas import IncidentSchema, IncidentUpdateSchema
from sqlalchemy.exc import IntegrityError
from models import RegistrationMediumEnum, StatusEnum

incident_schema = IncidentSchema()
incidents_schema = IncidentSchema(many=True)

incident_update_schema = IncidentUpdateSchema()


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

        agent_id = incident_data["agent_id"]
        if not agent_id:
            return {"msg": "Agent ID is required"}, 400

        incident = Incident(
            description=incident_data["description"],
            date=incident_data["date"],
            registration_medium=registration_medium_enum,
            user_id=incident_data["user_id"],
            agent_id_creation=incident_data["agent_id"],
            agent_id_last_update=incident_data["agent_id"],
        )
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

        return incident_schema.dump(incident), 200


class GetIncidentsByUser(Resource):
    def get(self, user_id):
        incidents = Incident.query.filter_by(user_id=user_id).all()
        return incidents_schema.dump(incidents), 200


class Ping(Resource):
    def get(self):
        return {"status": "alive"}, 200
