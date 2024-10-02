import os
import requests
import random
import time
from flask_restful import Resource
from flask import request, jsonify
from models import db, Incident, IncidentSchema


VIEW_360_BASE_URL = os.getenv("VIEW_360_BASE_URL", "http://localhost:5003")


class ReportView(Resource):
    def get(self, user_id):
        # view_360_response = requests.get(
        #     f"{VIEW_360_BASE_URL}/users/{user_id}"
        # )

        # return {
        #     "message": view_360_response.json()
        # }

        # Simular tiempo de procesamiento
        time.sleep(random.uniform(0.1, 0.5))

        # Simular falla aleatoria
        if random.randint(1, 10) >= 3:
            return {"error": "Internal Server Error"}, 500

        return {"report": "Reporte generado exitosamente"}, 200


class Ping(Resource):
    def get(self):
        return {"status": "healthy"}
