from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from models import Client, Plan


class ClientSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Client
        include_relationships = True
        load_instance = True
        exclude = ("password",)

    id = fields.String()
    name = fields.String(required=True)
    email = fields.Email(required=True)
    company_name = fields.String(required=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class PlanSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Plan
        include_relationships = True
        load_instance = True

    id = fields.String()
    nombre = fields.String(required=True)
    descripcion = fields.String(required=True)


class ClientPlanSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Client
        include_relationships = False
        load_instance = True

    id = fields.String()
    nombre = fields.String(required=True)
    descripcion = fields.String(required=True)
