import uuid
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ChatbotState(Enum):
    WELCOME = "welcome"
    DESCRIPTION = "description"
    USER_ID = "user_id"
    CONFIRM = "confirm"
    COMPANY_NAME_SELECTION = "company_name_selection"
    INCIDENT_ID = "incident_id"


class ChatbotConversation(db.Model):
    __tablename__ = "chatbot_conversations"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
    user_id = db.Column(db.String(255), nullable=True)
    state = db.Column(db.Enum(ChatbotState), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )
    client_id = db.Column(db.String(36), nullable=True)
    incident_description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "state": self.state.value,
        }
