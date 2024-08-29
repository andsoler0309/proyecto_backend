from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum as SQLAEnum
from enum import Enum


db = SQLAlchemy()


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"


class UserToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(SQLAEnum(UserRole), nullable=False)


class AdminCadenaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserToken
        include_relationships = True
        load_instance = True

    id = fields.String()