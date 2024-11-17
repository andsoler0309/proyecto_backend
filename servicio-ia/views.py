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

GESTOR_CLIENTES_BASE_URL = os.environ.get(
    "GESTOR_CLIENTES_BASE_URL", "http://localhost:5001"
)


REPORT_MESSAGES = {
    "en": {
        "incidents": "Reported incidents include system interruptions, data issues, and other critical errors affecting service performance and availability.",
        "compliance": "Compliance checks indicate a good percentage of resolved incidents.",
        "time": "Time analysis includes response times, processing times, and overall performance metrics to ensure efficient operations.",
        "total_incidents": "The total number of reported incidents is 100. It is recommended to hire more staff in the future to handle the workload.",
        "total_open_incidents": "The total number of open incidents is 50. It is recommended to prioritize resolving these incidents to prevent service interruptions.",
        "total_closed_incidents": "The total number of closed incidents is 50. It is recommended to perform a detailed analysis of resolved incidents to identify patterns and prevent future interruptions.",
        "average_resolution_time": "The average incident resolution time is 5 days. It is recommended to establish a resolution time target and monitor performance to improve efficiency.",
        "average_response_time": "The average incident response time is 2 hours. It is recommended to implement an incident prioritization system to ensure timely response to critical issues.",
        "total_phone_incidents": "The total number of incidents reported by phone is 30. It is recommended to improve the accessibility and quality of phone support to meet user needs.",
        "total_email_incidents": "The total number of incidents reported by email is 40. It is recommended to optimize email communication processes for faster incident resolution.",
        "total_chat_incidents": "The total number of incidents reported by chat is 30. It is recommended to improve chat support efficiency and quality for a better user experience.",
        "compliance_rate": "The compliance rate for resolved incidents is 80%. It is recommended to establish an incident review and validation process to ensure resolution quality and accuracy.",
        "invalid_report": "The specified report type is not recognized. Please check the input and try again."
    },
    "es": {
        "incidents": "Los incidentes reportados incluyen interrupciones del sistema, problemas de datos y otros errores críticos que afectan el rendimiento y la disponibilidad del servicio.",
        "compliance": "Las verificaciones de cumplimiento indican un buen porcentaje de incidentes resueltos.",
        "time": "El análisis de tiempo incluye tiempos de respuesta, tiempos de procesamiento y métricas de rendimiento general para garantizar operaciones eficientes.",
        "total_incidents": "El número total de incidentes reportados es de 100. Se recomienda que en un futuro se contrate más personal para manejar la carga de trabajo.",
        "total_open_incidents": "El número total de incidentes abiertos es de 50. Se recomienda priorizar la resolución de estos incidentes para evitar interrupciones en el servicio.",
        "total_closed_incidents": "El número total de incidentes cerrados es de 50. Se recomienda realizar un análisis detallado de los incidentes resueltos para identificar patrones y prevenir futuras interrupciones.",
        "average_resolution_time": "El tiempo promedio de resolución de incidentes es de 5 días. Se recomienda establecer un objetivo de tiempo de resolución y monitorear el rendimiento para mejorar la eficiencia.",
        "average_response_time": "El tiempo promedio de respuesta a incidentes es de 2 horas. Se recomienda implementar un sistema de priorización de incidentes para garantizar una respuesta oportuna a problemas críticos.",
        "total_phone_incidents": "El número total de incidentes reportados por teléfono es de 30. Se recomienda mejorar la accesibilidad y la calidad del soporte telefónico para satisfacer las necesidades de los usuarios.",
        "total_email_incidents": "El número total de incidentes reportados por correo electrónico es de 40. Se recomienda optimizar los procesos de comunicación por correo electrónico para una resolución más rápida de los incidentes.",
        "total_chat_incidents": "El número total de incidentes reportados por chat es de 30. Se recomienda mejorar la eficiencia y la calidad del soporte por chat para una mejor experiencia del usuario.",
        "compliance_rate": "La tasa de cumplimiento de incidentes resueltos es del 80%. Se recomienda establecer un proceso de revisión y validación de incidentes para garantizar la calidad y precisión de las resoluciones.",
        "invalid_report": "El tipo de informe especificado no se reconoce. Por favor, revise la entrada e intente de nuevo."
    },
    "fr": {
        "incidents": "Les incidents signalés comprennent des interruptions système, des problèmes de données et d'autres erreurs critiques affectant les performances et la disponibilité du service.",
        "compliance": "Les vérifications de conformité indiquent un bon pourcentage d'incidents résolus.",
        "time": "L'analyse temporelle comprend les temps de réponse, les temps de traitement et les métriques de performance globale pour assurer des opérations efficaces.",
        "total_incidents": "Le nombre total d'incidents signalés est de 100. Il est recommandé d'embaucher plus de personnel à l'avenir pour gérer la charge de travail.",
        "total_open_incidents": "Le nombre total d'incidents ouverts est de 50. Il est recommandé de prioriser la résolution de ces incidents pour éviter les interruptions de service.",
        "total_closed_incidents": "Le nombre total d'incidents clôturés est de 50. Il est recommandé d'effectuer une analyse détaillée des incidents résolus pour identifier les modèles et prévenir les interruptions futures.",
        "average_resolution_time": "Le temps moyen de résolution des incidents est de 5 jours. Il est recommandé d'établir un objectif de temps de résolution et de surveiller les performances pour améliorer l'efficacité.",
        "average_response_time": "Le temps moyen de réponse aux incidents est de 2 heures. Il est recommandé de mettre en place un système de priorisation des incidents pour assurer une réponse rapide aux problèmes critiques.",
        "total_phone_incidents": "Le nombre total d'incidents signalés par téléphone est de 30. Il est recommandé d'améliorer l'accessibilité et la qualité du support téléphonique pour répondre aux besoins des utilisateurs.",
        "total_email_incidents": "Le nombre total d'incidents signalés par email est de 40. Il est recommandé d'optimiser les processus de communication par email pour une résolution plus rapide des incidents.",
        "total_chat_incidents": "Le nombre total d'incidents signalés par chat est de 30. Il est recommandé d'améliorer l'efficacité et la qualité du support par chat pour une meilleure expérience utilisateur.",
        "compliance_rate": "Le taux de conformité des incidents résolus est de 80%. Il est recommandé d'établir un processus de révision et de validation des incidents pour garantir la qualité et la précision des résolutions.",
        "invalid_report": "Le type de rapport spécifié n'est pas reconnu. Veuillez vérifier l'entrée et réessayer."
    },
    "ar": {
        "incidents": "تشمل الحوادث المبلغ عنها انقطاع النظام ومشكلات البيانات وأخطاء حرجة أخرى تؤثر على أداء الخدمة وتوافرها.",
        "compliance": "تشير عمليات التحقق من الامتثال إلى نسبة جيدة من الحوادث التي تم حلها.",
        "time": "يشمل التحليل الزمني أوقات الاستجابة وأوقات المعالجة ومقاييس الأداء العامة لضمان العمليات الفعالة.",
        "total_incidents": "إجمالي عدد الحوادث المبلغ عنها هو 100. يوصى بتوظيف المزيد من الموظفين في المستقبل للتعامل مع عبء العمل.",
        "total_open_incidents": "إجمالي عدد الحوادث المفتوحة هو 50. يوصى بإعطاء الأولوية لحل هذه الحوادث لمنع انقطاع الخدمة.",
        "total_closed_incidents": "إجمالي عدد الحوادث المغلقة هو 50. يوصى بإجراء تحليل مفصل للحوادث التي تم حلها لتحديد الأنماط ومنع الانقطاعات المستقبلية.",
        "average_resolution_time": "متوسط وقت حل الحوادث هو 5 أيام. يوصى بتحديد هدف وقت الحل ومراقبة الأداء لتحسين الكفاءة.",
        "average_response_time": "متوسط وقت الاستجابة للحوادث هو ساعتان. يوصى بتنفيذ نظام تحديد أولويات الحوادث لضمان الاستجابة السريعة للمشكلات الحرجة.",
        "total_phone_incidents": "إجمالي عدد الحوادث المبلغ عنها عبر الهاتف هو 30. يوصى بتحسين إمكانية الوصول وجودة الدعم الهاتفي لتلبية احتياجات المستخدمين.",
        "total_email_incidents": "إجمالي عدد الحوادث المبلغ عنها عبر البريد الإلكتروني هو 40. يوصى بتحسين عمليات التواصل عبر البريد الإلكتروني لتسريع حل الحوادث.",
        "total_chat_incidents": "إجمالي عدد الحوادث المبلغ عنها عبر الدردشة هو 30. يوصى بتحسين كفاءة وجودة دعم الدردشة لتحسين تجربة المستخدم.",
        "compliance_rate": "معدل الامتثال للحوادث التي تم حلها هو 80%. يوصى بإنشاء عملية مراجعة وتحقق من الحوادث لضمان جودة ودقة الحلول.",
        "invalid_report": "نوع التقرير المحدد غير معروف. يرجى التحقق من المدخلات والمحاولة مرة أخرى."
    }
}

# Multilingual messages dictionary
MESSAGES = {
    "en": {
        "welcome": "Hello, welcome to the incident management chatbot. Please select an option:\n1. Create new incident\n2. Consult existing incident",
        "select_company": "Please select the number of the company for which you want to register an incident:\n{}",
        "describe_incident": "Please describe the incident you want to register",
        "confirm_description": "Understood, do you want to register the incident with the following description: {}?",
        "enter_id": "Please enter your identification number without spaces or dots",
        "enter_incident_id": "Please enter the incident ID you want to consult",
        "invalid_number": "The identification number must be a number",
        "not_understood": "I didn't understand your response, please start again with 'start'",
        "error_creating": "Error creating chatbot conversation",
        "error_updating": "Error updating chatbot conversation",
        "conversation_not_found": "Chatbot conversation not found",
        "missing_field": "Missing required field: {}",
        "error_incidents": "Error communicating with Incidents Service"
    },
    "es": {
        "welcome": "Hola, bienvenido al chatbot de gestión de incidentes. Por favor selecciona una opción:\n1. Crear nuevo incidente\n2. Consultar incidente existente",
        "select_company": "Por favor selecciona el número de la empresa para la cual quieres registrar un incidente:\n{}",
        "describe_incident": "Por favor describe el incidente que quieres registrar",
        "confirm_description": "Entendido, ¿quieres registrar el incidente con la siguiente descripción: {}?",
        "enter_id": "Por favor ingresa tu número de identificación sin espacios ni puntos",
        "enter_incident_id": "Por favor ingresa el ID del incidente que quieres consultar",
        "invalid_number": "El número de identificación debe ser un número",
        "not_understood": "No entendí tu respuesta, vuelve a iniciar con 'start'",
        "error_creating": "Error al crear la conversación del chatbot",
        "error_updating": "Error al actualizar la conversación del chatbot",
        "conversation_not_found": "Conversación de chatbot no encontrada",
        "missing_field": "Falta el campo requerido: {}",
        "error_incidents": "Error al comunicarse con el Servicio de Incidentes"
    },
    "fr": {
        "welcome": "Bonjour, bienvenue sur le chatbot de gestion des incidents. Veuillez sélectionner une option:\n1. Créer un nouvel incident\n2. Consulter un incident existant",
        "select_company": "Veuillez sélectionner le numéro de l'entreprise pour laquelle vous souhaitez enregistrer un incident:\n{}",
        "describe_incident": "Veuillez décrire l'incident que vous souhaitez enregistrer",
        "confirm_description": "Compris, voulez-vous enregistrer l'incident avec la description suivante : {}?",
        "enter_id": "Veuillez entrer votre numéro d'identification sans espaces ni points",
        "enter_incident_id": "Veuillez entrer l'ID de l'incident que vous souhaitez consulter",
        "invalid_number": "Le numéro d'identification doit être un nombre",
        "not_understood": "Je n'ai pas compris votre réponse, veuillez recommencer avec 'start'",
        "error_creating": "Erreur lors de la création de la conversation du chatbot",
        "error_updating": "Erreur lors de la mise à jour de la conversation du chatbot",
        "conversation_not_found": "Conversation du chatbot non trouvée",
        "missing_field": "Champ requis manquant : {}",
        "error_incidents": "Erreur de communication avec le Service des Incidents"
    },
    "ar": {
        "welcome": "مرحباً، مرحباً بك في روبوت الدردشة لإدارة الحوادث. يرجى اختيار خيار:\n1. إنشاء حادث جديد\n2. استشارة حادث موجود",
        "select_company": "يرجى اختيار رقم الشركة التي تريد تسجيل الحادث لها:\n{}",
        "describe_incident": "يرجى وصف الحادث الذي تريد تسجيله",
        "confirm_description": "مفهوم، هل تريد تسجيل الحادث بالوصف التالي: {}؟",
        "enter_id": "يرجى إدخال رقم الهوية الخاص بك بدون مسافات أو نقاط",
        "enter_incident_id": "يرجى إدخال معرف الحادث الذي تريد استشارته",
        "invalid_number": "يجب أن يكون رقم الهوية رقماً",
        "not_understood": "لم أفهم ردك، يرجى البدء مرة أخرى باستخدام 'start'",
        "error_creating": "خطأ في إنشاء محادثة روبوت الدردشة",
        "error_updating": "خطأ في تحديث محادثة روبوت الدردشة",
        "conversation_not_found": "لم يتم العثور على محادثة روبوت الدردشة",
        "missing_field": "حقل مطلوب مفقود: {}",
        "error_incidents": "خطأ في الاتصال بخدمة الحوادث"
    }
}


class UnifiedChatbot(Resource):
    def get_clients(self):
        try:
            clients_response = requests.get(
                f"{GESTOR_CLIENTES_BASE_URL}/clients",
                timeout=900,
            )
            if clients_response.status_code != 200:
                current_app.logger.error(
                    f"Error fetching incidents: {clients_response.text}"
                )
                return None
            return clients_response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return None

    def post(self):
        data = request.get_json()
        try:
            message = data["message"]
            language = data.get("language", "es")  # Default to Spanish if not specified
            if language not in MESSAGES:
                language = "es"  # Fallback to Spanish for unsupported languages
        except KeyError as e:
            return {"msg": MESSAGES[language]["missing_field"].format(str(e))}, 400

        if message == "start":
            chatbot_conversation = ChatbotConversation(
                state=ChatbotState.ACTION_SELECTION,
                language=language
            )
            db.session.add(chatbot_conversation)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return {"msg": MESSAGES[language]["error_creating"]}, 500

            return {
                "msg": MESSAGES[language]["welcome"],
                "chatbot_conversation_id": chatbot_conversation.id,
            }, 200

        try:
            chatbot_conversation_id = data["chatbot_conversation_id"]
        except KeyError as e:
            return {"msg": MESSAGES[language]["missing_field"].format(str(e))}, 400

        chatbot_conversation = ChatbotConversation.query.get(chatbot_conversation_id)
        if not chatbot_conversation:
            return {"msg": MESSAGES[language]["conversation_not_found"]}, 404

        language = chatbot_conversation.language
        chatbot_state = chatbot_conversation.state

        if chatbot_state == ChatbotState.ACTION_SELECTION:
            if message not in ["1", "2"]:
                return {"msg": MESSAGES[language]["not_understood"]}, 400

            if message == "1":  # Create incident
                clients = self.get_clients()
                companies = [cliente["company_name"] for cliente in clients]
                companies_numbered = "\n".join(
                    [f"{i+1}. {company}" for i, company in enumerate(companies)]
                )

                chatbot_conversation.state = ChatbotState.COMPANY_NAME_SELECTION
                db.session.add(chatbot_conversation)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    return {"msg": MESSAGES[language]["error_updating"]}, 500

                return {
                    "msg": MESSAGES[language]["select_company"].format(companies_numbered)
                }, 200
            else:  # Consult incident
                chatbot_conversation.state = ChatbotState.INCIDENT_ID
                db.session.add(chatbot_conversation)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    return {"msg": MESSAGES[language]["error_updating"]}, 500

                return {"msg": MESSAGES[language]["enter_incident_id"]}, 200

        # Handle company selection
        if chatbot_state == ChatbotState.COMPANY_NAME_SELECTION:
            company_number_selected = int(message) - 1
            clients = self.get_clients()
            if not clients:
                return {"msg": MESSAGES[language]["error_incidents"]}, 503

            client_id = clients[company_number_selected]["id"]
            chatbot_conversation.state = ChatbotState.DESCRIPTION
            chatbot_conversation.client_id = client_id
            db.session.add(chatbot_conversation)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return {"msg": MESSAGES[language]["error_updating"]}, 500

            return {"msg": MESSAGES[language]["describe_incident"]}, 200

        # Handle incident description
        if chatbot_state == ChatbotState.DESCRIPTION:
            chatbot_conversation.state = ChatbotState.CONFIRM
            chatbot_conversation.incident_description = message
            db.session.add(chatbot_conversation)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return {"msg": MESSAGES[language]["error_updating"]}, 500

            return {
                "msg": MESSAGES[language]["confirm_description"].format(message)
            }, 200

        # Handle confirmation
        if chatbot_state == ChatbotState.CONFIRM:
            if message.lower() in ["yes", "si", "oui", "نعم"]:
                chatbot_conversation.state = ChatbotState.USER_ID
                db.session.add(chatbot_conversation)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    return {"msg": MESSAGES[language]["error_updating"]}, 500

                return {"msg": MESSAGES[language]["enter_id"]}, 200
            else:
                chatbot_conversation.state = ChatbotState.DESCRIPTION
                db.session.add(chatbot_conversation)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    return {"msg": MESSAGES[language]["error_updating"]}, 500

                return {"msg": MESSAGES[language]["describe_incident"]}, 200

        # Handle user ID input
        if chatbot_state == ChatbotState.USER_ID:
            try:
                user_id = int(message)
            except ValueError:
                return {"msg": MESSAGES[language]["invalid_number"]}, 400

            chatbot_conversation.user_id = user_id
            chatbot_conversation.state = ChatbotState.WELCOME
            db.session.add(chatbot_conversation)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return {"msg": MESSAGES[language]["error_updating"]}, 500

            incident = {
                "description": chatbot_conversation.incident_description,
                "date": "2024-08-11",
                "registration_medium": "CHAT",
                "user_id": user_id,
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
                return {"msg": MESSAGES[language]["error_incidents"]}, 503

            return incidents_response.json(), incidents_response.status_code

        # Handle incident ID input for consultation
        if chatbot_state == ChatbotState.INCIDENT_ID:
            incident_id = message
            chatbot_conversation.state = ChatbotState.WELCOME
            db.session.add(chatbot_conversation)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return {"msg": MESSAGES[language]["error_updating"]}, 500

            try:
                incident_response = requests.get(
                    f"{GESTOR_INCIDENTES_BASE_URL}/incidents/{incident_id}",
                    timeout=900,
                )
                if incident_response.status_code != 200:
                    return incident_response.json(), incident_response.status_code
                return incident_response.json(), 200
            except requests.exceptions.RequestException as e:
                current_app.logger.error(
                    f"Error communicating with Incidents Service: {e}"
                )
                return {"msg": MESSAGES[language]["error_incidents"]}, 503

        return {"msg": MESSAGES[language]["not_understood"]}, 400


class Ping(Resource):
    def get(self):
        return {"status": "alive"}, 200


class Chatbot(Resource):
    def get_clients(self):
        try:
            clients_response = requests.get(
                f"{GESTOR_CLIENTES_BASE_URL}/clients",
                timeout=900,
            )
            if clients_response.status_code != 200:
                current_app.logger.error(
                    f"Error fetching incidents: {clients_response.text}"
                )
                return {"msg": "Error fetching incidents"}, 500
            clients = clients_response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Incidents Service: {e}")
            return {"msg": "Error communicating with Incidents Service"}, 503

        return clients

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
            
            clients = self.get_clients()
            companies = [cliente["company_name"] for cliente in clients]
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
            clients = self.get_clients()
            client_id = clients[company_number_selected]["id"]

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
    

class ReportLanguages(Resource):
    def get_message_key(self, user_message):
        """Helper method to determine the message key based on user input"""
        if "incidentes" in user_message or "incidents" in user_message or "حوادث" in user_message or "incidents" in user_message:
            return "incidents"
        elif "compliance" in user_message or "cumplimiento" in user_message or "conformité" in user_message or "امتثال" in user_message:
            return "compliance"
        elif "tiempo" in user_message or "time" in user_message or "temps" in user_message or "وقت" in user_message:
            return "time"
        elif user_message in [
            "total_incidents", "total_open_incidents", "total_closed_incidents",
            "average_resolution_time", "average_response_time", "total_phone_incidents",
            "total_email_incidents", "total_chat_incidents", "compliance_rate"
        ]:
            return user_message
        return "invalid_report"

    def post(self, client_id):
        body = request.get_json()
        user_message = body.get("user_message")
        language = body.get("language", "es")  # Default to Spanish if not specified
        
        # Validate language
        if language not in REPORT_MESSAGES:
            language = "es"  # Fallback to Spanish for unsupported languages
        
        # Get the appropriate message key
        message_key = self.get_message_key(user_message)
        
        # Get the message in the requested language
        message = REPORT_MESSAGES[language][message_key]
        
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
