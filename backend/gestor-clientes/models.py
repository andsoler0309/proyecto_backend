import enum
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import Enum as SQLAEnum
from enum import Enum

db = SQLAlchemy()


class ClientRole(Enum):
    ADMIN = "admin"
    USER = "user"


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    role = db.Column(SQLAEnum(ClientRole), nullable=False)


class ClientSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Client
        include_relationships = True
        load_instance = True
