from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from datetime import datetime
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


class TokenBlacklist(db.Model):
    __tablename__ = 'token_blacklist'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(255), unique=True, nullable=False)  # JWT ID
    token = db.Column(db.Text, nullable=False)
    blacklisted_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TokenBlacklist {self.jti}>"
