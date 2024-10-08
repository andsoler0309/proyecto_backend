import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "you-will-never-guess"
    GESTOR_AGENTES_BASE_URL = (
        os.getenv("GESTOR_AGENTES_BASE_URL") or "http://localhost:5001"
    )
    GESTOR_INCIDENTES_BASE_URL = (
        os.getenv("GESTOR_INCIDENTES_BASE_URL") or "http://localhost:5002"
    )
    GESTOR_CLIENTES_BASE_URL = (
        os.getenv("GESTOR_CLIENTES_BASE_URL") or "http://localhost:5003"
    )
    SERVICIO_IA_BASE_URL = os.getenv("SERVICIO_IA_BASE_URL") or "http://localhost:5005"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///api_gateway.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
