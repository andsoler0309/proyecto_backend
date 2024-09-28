import uuid
from datetime import datetime
from enum import Enum

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    AGENT = "agent"


class Verification(db.Model):
    __tablename__ = "verifications"

    verification_id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
    agent_id = db.Column(db.String(36), nullable=False)
    security_question = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Verification {self.verification_id} for Agent {self.agent_id}>"


class TokenBlacklist(db.Model):
    __tablename__ = "token_blacklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(255), unique=True, nullable=False)  # JWT ID
    token = db.Column(db.Text, nullable=False)
    blacklisted_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TokenBlacklist {self.jti}>"


class Session(db.Model):
    __tablename__ = "sessions"

    session_id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
    agent_id = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    last_activity = db.Column(db.DateTime, nullable=False)
    ip_address = db.Column(db.String(255))
    user_agent = db.Column(db.String(255))

    def __repr__(self):
        return f"<Session {self.session_id} for Agent {self.agent_id}>"


class FailedAttempt(db.Model):
    __tablename__ = "failed_attempts"

    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(36), nullable=False)
    attempts = db.Column(db.Integer, default=0)
    last_attempt = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<FailedAttempt for Agent {self.agent_id}>"


class AgentIPAddress(db.Model):
    __tablename__ = "agent_ip_addresses"

    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(36), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    first_used = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime, default=datetime.utcnow)
    login_count = db.Column(db.Integer, default=1)

    __table_args__ = (
        db.UniqueConstraint("agent_id", "ip_address", name="unique_agent_ip"),
    )

    def __repr__(self):
        return f"<AgentIPAddress {self.ip_address} for Agent {self.agent_id}>"


class IPAddressLoginAttempt(db.Model):
    __tablename__ = "ip_address_login_attempts"

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False, unique=True)
    attempts = db.Column(db.Integer, default=1)
    last_attempt = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<IPAddressLoginAttempt {self.ip_address}>"
