import os
import requests
from flask_restful import Resource
from flask import request
from models import db, Incident, IncidentSchema


VIEW_360_BASE_URL = os.getenv("VIEW_360_BASE_URL", "http://localhost:5003")


class ReportView(Resource):
    def get(self, user_id):
        view_360_response = requests.get(
            f"{VIEW_360_BASE_URL}/get_user"
        )

        return {
            "message": view_360_response.json()
        }


class Ping(Resource):
    def get(self):
        return {
            "status": "healthy"
        }
