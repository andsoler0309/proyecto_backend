from flask import request, current_app
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from enum import Enum
import datetime
import requests
from models import ChatbotState, ChatbotConversation, db
from schemas import ChatbotConversationSchema
import os


GESTOR_INCIDENTES_BASE_URL = os.environ.get(
    "GESTOR_INCIDENTES_BASE_URL", "http://localhost:5001"
)

clientes_data_mock = [
    {
        "id": "asd",
        "name": "Juan Perez",
        "email": "test@test.com",
        "password": "123",
        "company_name": "Company 1",
    },
    {
        "id": "qwe",
        "name": "Maria Rodriguez",
        "email": "test@test.com",
        "password": "123",
        "company_name": "Company 2",
    },
    {
        "id": "zxc",
        "name": "Pedro Martinez",
        "email": "test@test.com",
        "password": "123",
        "company_name": "Company 3",
    },
]


class Ping(Resource):
    def get(self):
        return {"status": "alive"}, 200


class Chatbot(Resource):
    def post(self):
        data = request.get_json()
        chatbot_state = None
        try:
            message = data["message"]
        except KeyError as e:
            return {"msg": f"Missing required field: {str(e)}"}, 400

        if message == "start":
            chatbot_conversation = ChatbotConversation(
                state=ChatbotState.COMPANY_NAME_SELECTION,
            )
            db.session.add(chatbot_conversation)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return {"msg": "Error creating chatbot conversation"}, 500

            companies = [cliente["company_name"] for cliente in clientes_data_mock]
            companies_numbered = "\n".join(
                [f"{i+1}. {company}" for i, company in enumerate(companies)]
            )
            return {
                "msg": f"Hola, bienvenido al chatbot de incidentes, porfavor selecciona el numero de la empresa a la cual quieres registrar un incidente:\n{companies_numbered}",
                "chatbot_conversation_id": chatbot_conversation.id,
            }, 200
        else:
            try:
                chatbot_conversation_id = data["chatbot_conversation_id"]
            except KeyError as e:
                return {"msg": f"Missing required field: {str(e)}"}, 400

            chatbot_conversation = ChatbotConversation.query.get(
                chatbot_conversation_id
            )
            if not chatbot_conversation:
                return {"msg": "Chatbot conversation not found"}, 404

            chatbot_state = chatbot_conversation.state

        if chatbot_state == ChatbotState.COMPANY_NAME_SELECTION:
            company_number_selected = int(message) - 1
            client_id = clientes_data_mock[company_number_selected]["id"]

            chatbot_conversation.state = ChatbotState.DESCRIPTION
            chatbot_conversation.client_id = client_id
            db.session.add(chatbot_conversation)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return {"msg": "Error updating chatbot conversation"}, 500

            return {
                "msg": "listo, ahora porfavor describe el incidente que quieres registrar"
            }, 200

        if chatbot_state == ChatbotState.DESCRIPTION:
            chatbot_conversation.state = ChatbotState.CONFIRM
            chatbot_conversation.incident_description = message
            db.session.add(chatbot_conversation)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return {"msg": "Error updating chatbot conversation"}, 500
            return {
                "msg": f"Entendido, quieres registrar el incidente con la siguiente descripción: {message}?"
            }, 200

        if chatbot_state == ChatbotState.CONFIRM:
            if message.lower() == "si":
                chatbot_conversation.state = ChatbotState.USER_ID
                db.session.add(chatbot_conversation)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    return {"msg": "Error updating chatbot conversation"}, 500

                return {
                    "msg": "Porfavor ingresa tu numero de identificacion sin espacios ni puntos"
                }, 200
            else:
                chatbot_conversation.state = ChatbotState.DESCRIPTION
                db.session.add(chatbot_conversation)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    return {"msg": "Error updating chatbot conversation"}, 500

                return {
                    "msg": "Porfavor describe el incidente que quieres registrar"
                }, 200

        if chatbot_state == ChatbotState.USER_ID:
            try:
                message = int(message)
            except ValueError:
                return {"msg": "El numero de identificacion debe ser un numero"}, 400

            chatbot_conversation.user_id = message
            chatbot_conversation.state = ChatbotState.WELCOME
            db.session.add(chatbot_conversation)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return {"msg": "Error updating chatbot conversation"}, 500

            incident = {
                "description": chatbot_conversation.incident_description,
                "date": "2024-08-11",
                "registration_medium": "CHAT",
                "user_id": message,
                "client_id": chatbot_conversation.client_id,
            }

            print(incident)
            try:
                incidents_response = requests.post(
                    f"{GESTOR_INCIDENTES_BASE_URL}/incidents",
                    json=incident,
                    timeout=900,
                )
                print(incidents_response)
            except requests.exceptions.RequestException as e:
                current_app.logger.error(
                    f"Error communicating with Incidents Service: {e}"
                )
                return {"msg": "Error communicating with Incidents Service"}, 503

            return incidents_response.json(), incidents_response.status_code


class Report(Resource):
    def post(self, client_id):
        message = "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum"
        return {"msg": message}, 200


class Incident(Resource):
    def get(self, incident_id):
        try:
            incident_response = requests.get(
                f"{GESTOR_INCIDENTES_BASE_URL}/incidents/{incident_id}",
                timeout=900,
            )
            if incident_response.status_code != 200:
                return incident_response.json(), incident_response.status_code
            incident = incident_response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        response = {
            "incident_id": incident["id"],
            "description": incident["description"],
            "possible_solution": "lore ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore",
        }

        return response, 200
