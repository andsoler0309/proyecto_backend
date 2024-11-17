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
        elif chatbot_state == ChatbotState.CONFIRM:
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
        elif chatbot_state == ChatbotState.USER_ID:
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

            try:
                incidents_response = requests.post(
                    f"{GESTOR_INCIDENTES_BASE_URL}/incidents",
                    json=incident,
                    timeout=900,
                )
            except requests.exceptions.RequestException as e:
                current_app.logger.error(
                    f"Error communicating with Incidents Service: {e}"
                )
                return {"msg": "Error communicating with Incidents Service"}, 503

            return incidents_response.json(), incidents_response.status_code
        else:
            return {"msg": "No entendi tu respuesta, vuelve a iniciar con start"}, 400


class IncidentChatbot(Resource):
    def post(self):
        data = request.get_json()
        chatbot_state = None
        try:
            message = data["message"]
        except KeyError as e:
            return {"msg": f"Missing required field: {str(e)}"}, 400

        if message == "start":
            chatbot_conversation = ChatbotConversation(
                state=ChatbotState.INCIDENT_ID,
            )
            db.session.add(chatbot_conversation)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return {"msg": "Error creating chatbot conversation"}, 500

            return {
                "msg": f"Hola, bienvenido al chatbot de incidentes, porfavor ingresa el id del incidente que quieres consultar",
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

        if chatbot_state == ChatbotState.INCIDENT_ID:
            incident_id = message

            chatbot_conversation.state = ChatbotState.WELCOME
            db.session.add(chatbot_conversation)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return {"msg": "Error updating chatbot conversation"}, 500

            try:
                incident_response = requests.get(
                    f"{GESTOR_INCIDENTES_BASE_URL}/incidents/{incident_id}",
                    timeout=900,
                )
                if incident_response.status_code != 200:
                    return incident_response.json(), incident_response.status_code
                incident = incident_response.json()
            except requests.exceptions.RequestException as e:
                current_app.logger.error(
                    f"Error communicating with Incidents Service: {e}"
                )
                return {"msg": "Error communicating with Incidents Service"}, 503

            return incident, 200
        else:
            return {"msg": "No entendi tu respuesta, vuelve a iniciar con start"}, 400


class Report(Resource):
    def post(self, client_id):
        body = request.get_json()
        user_message = body.get("user_message")
        if "incidentes" in user_message:
            message = "Los incidentes reportados incluyen interrupciones del sistema, problemas de datos y otros errores críticos que afectan el rendimiento y la disponibilidad del servicio."
        elif "compliance" in user_message:
            message = "Las verificaciones de cumplimiento indican un buen porcentaje de incidentes resueltos."
        elif "tiempo" in user_message:
            message = "El análisis de tiempo incluye tiempos de respuesta, tiempos de procesamiento y métricas de rendimiento general para garantizar operaciones eficientes."
        elif user_message == "total_incidents":
            message = "El número total de incidentes reportados es de 100. Se recomienda que en un futuro se contrate más personal para manejar la carga de trabajo."
        elif user_message == "total_open_incidents":
            message = "El número total de incidentes abiertos es de 50. Se recomienda priorizar la resolución de estos incidentes para evitar interrupciones en el servicio."
        elif user_message == "total_closed_incidents":
            message = "El número total de incidentes cerrados es de 50. Se recomienda realizar un análisis detallado de los incidentes resueltos para identificar patrones y prevenir futuras interrupiones."
        elif user_message == "average_resolution_time":
            message = "El tiempo promedio de resolución de incidentes es de 5 días. Se recomienda establecer un objetivo de tiempo de resolución y monitorear el rendimiento para mejorar la eficiencia."
        elif user_message == "average_response_time":
            message = "El tiempo promedio de respuesta a incidentes es de 2 horas. Se recomienda implementar un sistema de priorización de incidentes para garantizar una respuesta oportuna a problemas críticos."
        elif user_message == "total_phone_incidents":
            message = "El número total de incidentes reportados por teléfono es de 30. Se recomienda mejorar la accesibilidad y la calidad del soporte telefónico para satisfacer las necesidades de los usuarios."
        elif user_message == "total_email_incidents":
            message = "El número total de incidentes reportados por correo electrónico es de 40. Se recomienda optimizar los procesos de comunicación por correo electrónico para una resolución más rápida de los incidentes."
        elif user_message == "total_chat_incidents":
            message = "El número total de incidentes reportados por chat es de 30. Se recomienda mejorar la eficiencia y la calidad del soporte por chat para una mejor experiencia del usuario."
        elif user_message == "compliance_rate":
            message = "La tasa de cumplimiento de incidentes resueltos es del 80%. Se recomienda establecer un proceso de revisión y validación de incidentes para garantizar la calidad y precisión de las resoluciones."
        else:
            message = "El tipo de informe especificado no se reconoce. Por favor, revise la entrada e intente de nuevo."

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

        description = incident["description"]
        if "ayuda" in description:
            possible_solution = "Para resolver este incidente, proporcione orientación adicional a los usuarios sobre cómo navegar y resolver problemas comunes. Puede ser útil un manual de usuario o un sistema de asistencia en línea."
        elif "error" in description:
            possible_solution = "Revise los errores potenciales en la configuración del sistema o de los datos. Verifique los registros de errores para identificar cualquier falla en la comunicación o discrepancias en los datos."
        elif "falla" in description:
            possible_solution = "Investigue posibles fallas en el sistema y revise los registros para un análisis detallado de la causa raíz. La revisión de hardware o red también podría ser necesaria si se identifican patrones recurrentes."
        else:
            possible_solution = "Consulte la documentación de soporte o póngase en contacto con el soporte técnico para recibir asistencia adicional en la resolución del incidente."

        response = {
            "incident_id": incident["id"],
            "description": incident["description"],
            "possible_solution": possible_solution,
        }

        return response, 200
