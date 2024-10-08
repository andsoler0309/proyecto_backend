import uuid
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class RegistrationMediumEnum(Enum):
    EMAIL = "email"
    PHONE = "phone"
    CHAT = "chat"


class StatusEnum(Enum):
    OPEN = "open"
    CLOSED = "closed"


class Incident(db.Model):
    __tablename__ = "incidents"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
    agent_id_creation = db.Column(db.String(36), nullable=True)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    registration_medium = db.Column(db.Enum(RegistrationMediumEnum), nullable=False)
    user_id = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )
    status = db.Column(db.Enum(StatusEnum), nullable=False, default=StatusEnum.OPEN)
    agent_id_last_update = db.Column(db.String(36), nullable=True)
    client_id = db.Column(db.String(36), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "description": self.description,
            "date": self.date.isoformat(),
            "registration_medium": self.registration_medium.value,
            "user_id": self.user_id,
            "status": self.status.value,
        }
