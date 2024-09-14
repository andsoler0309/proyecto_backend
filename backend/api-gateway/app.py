# app.py
from flask import Flask
from flask_restful import Api
from views import *
from config import Config
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db
import logging
from logging.handlers import RotatingFileHandler
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app_context = app.app_context()
    app_context.push()

    # Initialize Extensions
    db.init_app(app)
    db.create_all()
    # migrate = Migrate(app, db)

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    api = Api(app)

    # Register API resources
    api.add_resource(Login, '/agents/login', endpoint='login', methods=['POST'])
    api.add_resource(VerifySecurityAnswer, '/agents/verify-security-answer', endpoint='verify_security_answer', methods=['POST'])
    api.add_resource(ProtectedResource, '/protected', endpoint='protected', methods=['GET'])
    api.add_resource(RoleProtectedResource, '/role-protected', endpoint='role-protected', methods=['GET'])
    api.add_resource(Ping, '/api-gateway/ping', endpoint='ping', methods=['GET'])
    api.add_resource(CreateAgent, '/agents', endpoint='create_agent', methods=['POST'])
    api.add_resource(DeleteAgent, '/agents/<string:agent_id>', endpoint='delete_agent', methods=['DELETE'])
    api.add_resource(CreateIncident, '/incidents', endpoint='create_incident', methods=['POST'])
    api.add_resource(DeleteIncident, '/incidents/<string:incident_id>', endpoint='delete_incident', methods=['DELETE'])

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
