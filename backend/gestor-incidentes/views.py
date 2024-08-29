from flask_restful import Resource
from flask import request
from models import db, Incident, IncidentSchema
import os

VIEW_360_BASE_URL = os.getenv("VIEW_360_BASE_URL", "http://localhost:5003")


class IncidentsView(Resource):
    def post(self):
        return {"message": "incidente creado exitosamente"}, 201

    def get(self):
        return {
            "incidents": [
                {
                    "name": "incidente 1",
                    "description": "testeando"
                }
            ]
        }, 200


class IncidentView(Resource):
    def get(self, incident_id):
        print(VIEW_360_BASE_URL)
        return {"name": f"incidente {incident_id}", "description": "testeando"}, 200


class Ping(Resource):
    def get(self):
        return {
            "status": "healthy"
        }