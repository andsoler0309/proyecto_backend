from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
import uuid


db = SQLAlchemy()


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    AGENT = "agent"


class Verification(db.Model):
    __tablename__ = 'verifications'

    verification_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    agent_id = db.Column(db.String(36), nullable=False)
    security_question = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Verification {self.verification_id} for Agent {self.agent_id}>"
