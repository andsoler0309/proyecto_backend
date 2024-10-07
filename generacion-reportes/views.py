import os
import requests
import random
import time
from flask_restful import Resource
from flask import request, jsonify

# from models import db, Report
from config import Config


class Ping(Resource):
    def get(self):
        return {"status": "healthy"}, 200


class GenerateReport(Resource):
    def get(self, client_id):
        # get incidents data
        incident_response = requests.get(
            f"{Config.GESTOR_INCIDENTES_BASE_URL}/incidents/client/{client_id}",
            timeout=5,
        )
        if incident_response.status_code != 200:
            return incident_response.json(), incident_response.status_code
        incident = incident_response.json()

        # get client data
        client_response = requests.get(
            f"{Config.GESTOR_CLIENTES_BASE_URL}/clients/{client_id}",
            timeout=5,
        )
        if client_response.status_code != 200:
            return client_response.json(), client_response.status_code
        client = client_response.json()

        stats = {
            "total_incidents": len(incident),
            "total_open_incidents": len([i for i in incident if i["status"] == "OPEN"]),
            "total_closed_incidents": len(
                [i for i in incident if i["status"] == "CLOSED"]
            ),
            "average_resolution_time": f"{random.randint(1, 100)} days",
        }

        return {"client": client, "incidents": incident, "stats": stats}, 200
