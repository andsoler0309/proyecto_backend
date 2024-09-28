from flask import Flask
from flask_restful import Api
from models import db
from views import IncidentList, IncidentDetail, Ping
from flask_migrate import Migrate
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True

    app_context = app.app_context()
    app_context.push()

    db.init_app(app)
    migrate = Migrate(app, db)
    db.create_all()

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    api = Api(app)

    # Register API resources
    api.add_resource(IncidentList, '/incidents')
    api.add_resource(IncidentDetail, '/incidents/<string:incident_id>')
    api.add_resource(Ping, '/gestor-incidentes/ping')


    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)