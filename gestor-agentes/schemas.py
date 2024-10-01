from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from marshmallow_enum import EnumField
from models import Agent, UserRole


class AgentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Agent
        include_relationships = True
        load_instance = True
        exclude = ("password_hash",)

    id = fields.String()
    name = fields.String(required=True)
    email = fields.Email(required=True)
    role = EnumField(UserRole, required=True)
    identification = fields.String(required=True)
    phone = fields.String(required=True)
    address = fields.String(required=True)
    city = fields.String(required=True)
    state = fields.String(required=True)
    zip_code = fields.String(required=True)
    country = fields.String(required=True)
    is_locked = fields.Boolean()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
