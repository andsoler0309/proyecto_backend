from flask import request
from flask_restful import Resource
from models import db, Incident
from schemas import IncidentSchema
from sqlalchemy.exc import IntegrityError

incident_schema = IncidentSchema()
incidents_schema = IncidentSchema(many=True)


class IncidentList(Resource):
    def get(self):
        agent_id = request.args.get('agent_id')
        if agent_id:
            incidents = Incident.query.filter_by(agent_id=agent_id).all()
        else:
            incidents = Incident.query.all()
        return incidents_schema.dump(incidents), 200

    def post(self):
        data = request.get_json()
        try:
            incident_data = incident_schema.load(data)
        except Exception as e:
            return {"msg": "Invalid data", "error": str(e)}, 400

        incident = Incident(
            agent_id=incident_data['agent_id'],
            description=incident_data['description'],
            date=incident_data['date']
        )
        db.session.add(incident)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"msg": "Error creating incident"}, 500

        return incident_schema.dump(incident), 201


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


class Ping(Resource):
    def get(self):
        return {"status": "alive"}, 200
