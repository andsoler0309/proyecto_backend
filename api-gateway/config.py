import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "you-will-never-guess"
    JWT_SECRET = os.getenv("JWT_SECRET") or "your_jwt_secret_key"
    JWT_ALGORITHM = "HS256"
    JWT_EXP_DELTA_SECONDS = 3600  # 1 hour
    GESTOR_AGENTES_BASE_URL = (
        os.getenv("GESTOR_AGENTES_BASE_URL") or "http://localhost:5001"
    )
    GESTOR_INCIDENTES_BASE_URL = (
        os.getenv("GESTOR_INCIDENTES_BASE_URL") or "http://localhost:5002"
    )
    GESTOR_CLIENTES_BASE_URL = (
        os.getenv("GESTOR_CLIENTES_BASE_URL") or "http://localhost:5003"
    )
    GENERACION_REPORTES_BASE_URL = (
        os.getenv("GENERACION_REPORTES_BASE_URL") or "http://localhost:5004"
    )
    SERVICIO_IA_BASE_URL = os.getenv("SERVICIO_IA_BASE_URL") or "http://localhost:5005"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "your_openai_api_key"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///api_gateway.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_INACTIVITY_LIMIT = 30  # minutes
    MAX_FAILED_ATTEMPTS = 3
