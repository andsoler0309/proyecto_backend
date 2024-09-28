import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Incident(db.Model):
    __tablename__ = 'incidents'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    agent_id = db.Column(db.String(36), nullable=False)  # UUID as string
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "description": self.description,
            "date": self.date.isoformat()
        }
