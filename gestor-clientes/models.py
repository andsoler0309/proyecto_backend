import enum
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import Enum as SQLAEnum
from enum import Enum

db = SQLAlchemy()


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Plan {self.nombre}>'


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=True)
    plan = db.relationship('Plan', backref='users')

    def __repr__(self):
        return f'<User {self.email}>'
