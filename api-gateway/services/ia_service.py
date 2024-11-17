import requests
from flask import current_app, request
from flask_restful import Resource
from marshmallow import ValidationError
from config import Config
from schemas import ChatBotSchema

chat_bot_schema = ChatBotSchema()


class ChatBot(Resource):
    def post(self):
        data = request.get_json()
        try:
            validated_data = chat_bot_schema.load(data)
        except ValidationError as err:
            return {"msg": "Invalid data", "errors": err.messages}, 400

        try:
            chat_bot_response = requests.post(
                f"{Config.SERVICIO_IA_BASE_URL}/chatbot",
                json=validated_data,
                timeout=900,
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with ChatBot Service: {e}")
            return {"msg": "Error communicating with ChatBot Service"}, 503

        if chat_bot_response.status_code != 200:
            return chat_bot_response.json(), chat_bot_response.status_code

        return chat_bot_response.json(), 200


class UnifiedChatbot(Resource):
    def post(self):
        data = request.get_json()
        try:
            validated_data = chat_bot_schema.load(data)
        except ValidationError as err:
            return {"msg": "Invalid data", "errors": err.messages}, 400

        try:
            chat_bot_response = requests.post(
                f"{Config.SERVICIO_IA_BASE_URL}/unified-chatbot",
                json=validated_data,
                timeout=900,
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with ChatBot Service: {e}")
            return {"msg": "Error communicating with ChatBot Service"}, 503

        if chat_bot_response.status_code != 200:
            return chat_bot_response.json(), chat_bot_response.status_code

        return chat_bot_response.json(), 200


class IncidentChatBot(Resource):
    def post(self):
        data = request.get_json()
        try:
            validated_data = chat_bot_schema.load(data)
        except ValidationError as err:
            return {"msg": "Invalid data", "errors": err.messages}, 400

        try:
            chat_bot_response = requests.post(
                f"{Config.SERVICIO_IA_BASE_URL}/chatbot/incident",
                json=validated_data,
                timeout=900,
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with ChatBot Service: {e}")
            return {"msg": "Error communicating with ChatBot Service"}, 503

        if chat_bot_response.status_code != 200:
            return chat_bot_response.json(), chat_bot_response.status_code

        return chat_bot_response.json(), 200


class GetReportInsights(Resource):
    def post(self, client_id):
        data = request.get_json()
        try:
            chat_bot_response = requests.post(
                f"{Config.SERVICIO_IA_BASE_URL}/report/{client_id}",
                json=data,
                timeout=900,
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with ChatBot Service: {e}")
            return {"msg": "Error communicating with ChatBot Service"}, 503

        if chat_bot_response.status_code != 200:
            return chat_bot_response.json(), chat_bot_response.status_code

        return chat_bot_response.json(), 200
    

class GetReportInsightsLanguages(Resource):
    def post(self, client_id):
        data = request.get_json()
        try:
            chat_bot_response = requests.post(
                f"{Config.SERVICIO_IA_BASE_URL}/report-languages/{client_id}",
                json=data,
                timeout=900,
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with ChatBot Service: {e}")
            return {"msg": "Error communicating with ChatBot Service"}, 503

        if chat_bot_response.status_code != 200:
            return chat_bot_response.json(), chat_bot_response.status_code

        return chat_bot_response.json(), 200
