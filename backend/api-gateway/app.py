from flask import Flask, request
from flask_cors import CORS
from monitor import monitor_registration_errors
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity
from models import UserRole, db
import requests
import os

from token_service import roles_required

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config['JWT_SECRET_KEY'] = 'frase-secreta'
jwt = JWTManager(app)

GESTOR_CLIENTES_BASE_URL = os.getenv("GESTOR_CLIENTES_BASE_URL")
GENERACION_REPORTES_BASE_URL = os.getenv("GENERACION_REPORTES_BASE_URL")
GESTOR_INCIDENTES_BASE_URL = os.getenv("GESTOR_INCIDENTES_BASE_URL")
GESTOR_FIDELIZACION_BASE_URL = os.getenv("GESTOR_FIDELIZACION_BASE_URL")
DATABASE_URL = os.getenv("DATABASE_URL")


@app.route('/client/register', methods=['POST'])
@monitor_registration_errors
def register_candidate():
    response = requests.post(f'{GESTOR_CLIENTES_BASE_URL}/signin', json=request.json)
    return response.json(), response.status_code


@app.route('/client/login', methods=['POST'])
def login():
    response = requests.post(f'{GESTOR_CLIENTES_BASE_URL}/login', json=request.json, headers=dict(request.headers))

    if response.status_code == 200:
        user_data = response.json()
        role = UserRole(user_data['role']).value  # Ensuring the role is the enum value
        access_token = create_access_token(identity={'email': user_data['email'], 'role': role})

        response = response.json()
        response["access_token"] = access_token

        return response, 200
    else:
        return {"msg": "Bad username or password"}, 401


@app.route('/incidents', methods=['GET'])
@roles_required([UserRole.ADMIN])
def get_all_incidents():
    # current_user = get_jwt_identity()
    response = requests.get(f'{GESTOR_INCIDENTES_BASE_URL}/incidents', headers=dict(request.headers))
    return response.json(), response.status_code


@app.route('/user/<int:user_id>', methods=['GET'])
@roles_required([UserRole.ADMIN])
def get_user_information(user_id):
    response = requests.get(f'{GESTOR_FIDELIZACION_BASE_URL}/user/{user_id}', headers=dict(request.headers))
    return response.json(), response.status_code


@app.route('/api-gateway/ping', methods=['GET'])
def ping():
    return {
        "status": "healthy"
    }