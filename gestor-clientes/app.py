from flask import Flask
from flask_restful import Api
from models import db, Plan
from views import *
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
    db.create_all()

    # Crear las tablas y agregar planes si no existen
    with app.app_context():
        db.create_all()
        if Plan.query.count() == 0:
            plans = [
                Plan(
                    nombre="Emprendedor",
                    descripcion=(
                        "Servicio básico para empresas que desean atención telefónica a sus clientes o interesados. "
                        "Incluye registro de PQRs, atención telefónica por agentes, búsqueda en base de conocimientos, "
                        "y procesos de escalamiento automatizados."
                    ),
                ),
                Plan(
                    nombre="Empresario",
                    descripcion=(
                        "Servicio avanzado con múltiples canales de comunicación: teléfono, chatbot, app móvil, y correo electrónico. "
                        "Incluye todas las funcionalidades del plan Emprendedor más llamadas de salida, tablero de control para análisis, "
                        "y gestión avanzada de incidentes."
                    ),
                ),
                Plan(
                    nombre="Empresario Plus",
                    descripcion=(
                        "Servicio completo con todos los canales de atención del plan Empresario más capacidades de inteligencia artificial "
                        "y aprendizaje automático. Incluye análisis predictivo de PQRs, respuestas automáticas apoyadas por modelos analíticos, "
                        "y soporte para verticales específicas como telcos, retail, banca, entre otros."
                    ),
                ),
            ]
            db.session.add_all(plans)
            db.session.commit()

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    api = Api(app)

    # Register API resources
    api.add_resource(ClientRegistration, "/clients/register")
    api.add_resource(ClientLogin, "/clients/login")
    # api.add_resource(AgentDetail, '/agents/<string:agent_id>')
    # api.add_resource(AgentLock, '/agents/<string:agent_id>/lock')
    # api.add_resource(AgentUnlock, '/agents/<string:agent_id>/unlock')
    # api.add_resource(AgentReset, '/agents/<string:agent_id>/reset')
    api.add_resource(Ping, "/gestor-clientes/ping")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
