import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///api_gateway.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
