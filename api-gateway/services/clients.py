import requests
from flask import current_app, request
from flask_restful import Resource
from schemas import (
    ClientSchema,
    PlanSchema,
    ClientCreationSchema,
    ClientPlanSchema,
    ClientUpdateSchema,
    LoginSchema,
)
from marshmallow import ValidationError
from config import Config
from utils import generate_jwt_client
from auth import client_required

client_creation_schema = ClientCreationSchema()
client_schema = ClientSchema()
plan_schema = PlanSchema()
client_plan_schema = ClientPlanSchema()
login_schema = LoginSchema()
client_update_schema = ClientUpdateSchema()


class CreateClient(Resource):
    def post(self):
        data = request.get_json()
        try:
            validated_data = client_creation_schema.load(data)
        except ValidationError as err:
            return {"msg": "Invalid data", "errors": err.messages}, 400

        # Forward the client creation to Clients service
        try:
            clients_response = requests.post(
                f"{Config.GESTOR_CLIENTES_BASE_URL}/clients/register",
                json=validated_data,
                timeout=900,
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Clients Service: {e}")
            return {"msg": "Error communicating with Clients Service"}, 503

        if clients_response.status_code != 201:
            return clients_response.json(), clients_response.status_code

        return clients_response.json(), 201


class ClientLogin(Resource):
    def post(self):
        data = request.get_json()
        try:
            validated_data = login_schema.load(data)
        except ValidationError as err:
            return {"msg": "Invalid data", "errors": err.messages}, 400

        email = validated_data["email"]
        password = validated_data["password"]

        try:
            clients_response = requests.post(
                f"{Config.GESTOR_CLIENTES_BASE_URL}/clients/login",
                json={"email": email, "password": password},
                timeout=900,
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Gestor-cliente: {e}")
            return {"msg": "Error communicating with Gestor-cliente"}, 503

        if clients_response.status_code != 200:
            return {"msg": "Bad username or password"}, 401

        client_id = clients_response.json()["id"]
        token = generate_jwt_client(client_id)

        return {
            "msg": "Login successful",
            "token": token,
            "client_id": client_id,
        }, 200


class GetClient(Resource):
    @client_required
    def get(self, current_client, client_id):
        try:
            clients_response = requests.get(
                f"{Config.GESTOR_CLIENTES_BASE_URL}/clients/{client_id}",
                timeout=900,
            )
            if clients_response.status_code != 200:
                return clients_response.json(), clients_response.status_code
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Clients Service: {e}")
            return {"msg": "Error communicating with Clients Service"}, 503

        return clients_response.json(), 200


class GetClientPlan(Resource):
    def get(self, client_id):
        try:
            plan_response = requests.get(
                f"{Config.GESTOR_CLIENTES_BASE_URL}/clients/{client_id}/plan",
                timeout=900,
            )
            if plan_response.status_code != 200:
                return plan_response.json(), plan_response.status_code
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Clients Service: {e}")
            return {"msg": "Error communicating with Clients Service"}, 503

        return plan_response.json(), 200


class UpdateClient(Resource):
    @client_required
    def put(self, current_client, client_id):
        data = request.get_json()
        try:
            validated_data = client_update_schema.load(data)
        except ValidationError as err:
            return {"msg": "Invalid data", "errors": err.messages}, 400

        try:
            clients_response = requests.put(
                f"{Config.GESTOR_CLIENTES_BASE_URL}/clients/{client_id}",
                json=validated_data,
                timeout=900,
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Clients Service: {e}")
            return {"msg": "Error communicating with Clients Service"}, 503

        if clients_response.status_code != 200:
            return clients_response.json(), clients_response.status_code

        return clients_response.json(), 200


class UpdateClientPlan(Resource):
    @client_required
    def put(self, current_client, client_id):
        data = request.get_json()
        try:
            validated_data = client_plan_schema.load(data)
        except ValidationError as err:
            return {"msg": "Invalid data", "errors": err.messages}, 400

        try:
            plan_response = requests.put(
                f"{Config.GESTOR_CLIENTES_BASE_URL}/clients/{client_id}/plan",
                json=validated_data,
                timeout=900,
            )
            if plan_response.status_code != 200:
                return plan_response.json(), plan_response.status_code
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Clients Service: {e}")
            return {"msg": "Error communicating with Clients Service"}, 503

        return plan_response.json(), 200


class SelectClientPlan(Resource):
    @client_required
    def post(self, current_client, client_id, plan_id):
        try:
            plan_response = requests.post(
                f"{Config.GESTOR_CLIENTES_BASE_URL}/clients/{client_id}/plan/{plan_id}",
                timeout=900,
            )
            if plan_response.status_code != 200:
                return plan_response.json(), plan_response.status_code
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Clients Service: {e}")
            return {"msg": "Error communicating with Clients Service"}, 503

        return plan_response.json(), 200


class GetClientsByPlan(Resource):
    def get(self, plan_id):
        try:
            clients_response = requests.get(
                f"{Config.GESTOR_CLIENTES_BASE_URL}/clients/plan/{plan_id}",
                timeout=900,
            )
            if clients_response.status_code != 200:
                return clients_response.json(), clients_response.status_code
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Clients Service: {e}")
            return {"msg": "Error communicating with Clients Service"}, 503

        return clients_response.json


class GetPlans(Resource):
    def get(self):
        try:
            plans_response = requests.get(
                f"{Config.GESTOR_CLIENTES_BASE_URL}/plans",
                timeout=900,
            )
            if plans_response.status_code != 200:
                return plans_response.json(), plans_response.status_code
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Clients Service: {e}")
            return {"msg": "Error communicating with Clients Service"}, 503

        return plans_response.json(), 200


class getclients(Resource):
    def get(self):
        try:
            clients_response = requests.get(
                f"{Config.GESTOR_CLIENTES_BASE_URL}/clients",
                timeout=900,
            )
            if clients_response.status_code != 200:
                return clients_response.json(), clients_response.status_code
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Clients Service: {e}")
            return {"msg": "Error communicating with Clients Service"}, 503

        return clients_response.json(), 200
