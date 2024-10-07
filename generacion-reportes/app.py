import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from views import *
# from models import db
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app_context = app.app_context()
    app_context.push()

    # db.init_app(app)
    # db.create_all()

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    api = Api(app)

    # Register API resources
    api.add_resource(GenerateReport, "/reports/<string:client_id>")
    api.add_resource(Ping, "/gestor-incidentes/ping")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
