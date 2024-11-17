from flask import Flask
from flask_restful import Api
from views import *
from flask_cors import CORS
from models import db
import os


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True

    app_context = app.app_context()
    app_context.push()

    db.init_app(app)
    db.create_all()

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    api = Api(app)

    # Register API resources
    api.add_resource(Ping, "/servicio-ia/ping")
    api.add_resource(Chatbot, "/chatbot")
    api.add_resource(IncidentChatbot, "/chatbot/incident")
    api.add_resource(Report, "/report/<string:client_id>")
    api.add_resource(Incident, "/incident/<string:incident_id>")
    api.add_resource(UnifiedChatbot, "/unified-chatbot")
    api.add_resource(ReportLanguages, "/report-languages/<string:client_id>")
    api.add_resource(IncidentSolutionDescription, "/incident-solution")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
