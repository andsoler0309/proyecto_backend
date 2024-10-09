# app.py
from flask import Flask
from flask_restful import Api
from models import db
from views import *
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app_context = app.app_context()
    app_context.push()

    db.init_app(app)
    migrate = Migrate(app, db)
    db.create_all()

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    api = Api(app)

    # Register API resources
    api.add_resource(AgentRegistration, "/agents/register")
    api.add_resource(AgentLogin, "/agent/login")
    api.add_resource(AgentDetail, "/agents/<string:agent_id>")
    api.add_resource(AgentLock, "/agents/<string:agent_id>/lock")
    api.add_resource(AgentUnlock, "/agents/<string:agent_id>/unlock")
    api.add_resource(AgentReset, "/agents/<string:agent_id>/reset")
    api.add_resource(Ping, "/gestor-agentes/ping")
    api.add_resource(AdminList, "/agents/admins")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
