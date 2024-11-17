import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "tu_clave_secreta")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True
    PRIVACY_KEY = "6Ld9ZVQaAAAAAFTX6Q4Q4Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Za"
