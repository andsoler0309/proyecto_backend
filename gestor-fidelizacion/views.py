import requests
import os
from flask_restful import Resource

VIEW_360_BASE_URL = os.getenv("VIEW_360_BASE_URL", "http://localhost:5003")


class UserView(Resource):
    def get(self, user_id):
        view_360_response = requests.get(f"{VIEW_360_BASE_URL}/users/{user_id}")

        return {"message": view_360_response.json()}


class Ping(Resource):
    def get(self):
        return {"status": "healthy"}
