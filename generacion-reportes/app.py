import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from views import *
from models import db


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["VIEW_360_BASE_URL"] = os.getenv(
        "VIEW_360_BASE_URL", "http://localhost:5003"
    )
    app.config["GESTOR_INCIDENTES_BASE_URL"] = os.getenv(
        "GESTOR_INCIDENTES_BASE_URL", "http://localhost:5002"
    )
    app.config["GESTOR_CLIENTES_BASE_URL"] = os.getenv(
        "GESTOR_CLIENTES_BASE_URL", "http://localhost:5000"
    )
    app.config["GESTOR_AGENTES_BASE_URL"] = os.getenv(
        "GESTOR_AGENTES_BASE_URL", "http://localhost:5001"
    )

    app_context = app.app_context()
    app_context.push()

    db.init_app(app)
    db.create_all()

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    api = Api(app)

    # Register API resources
    # api.add_resource(IncidentList, "/incidents")
    api.add_resource(Ping, "/gestor-incidentes/ping")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
