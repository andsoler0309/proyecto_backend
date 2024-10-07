from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from enum import Enum
from models import RegistrationMediumEnum, StatusEnum


class IncidentSchema(Schema):
    id = fields.String(dump_only=True)
    agent_id = fields.String(required=True, load_only=True)
    agent_id_creation = fields.String(dump_only=True)
    description = fields.String(required=True)
    date = fields.Date(required=True)
    registration_medium = EnumField(RegistrationMediumEnum, required=True)
    user_id = fields.Int(required=True)
    status = EnumField(StatusEnum, dump_only=True)
    agent_id_last_update = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    client_id = fields.String(required=True)


class IncidentUpdateSchema(Schema):
    id = fields.String(dump_only=True)
    agent_id = fields.String(required=True, load_only=True)
    agent_id_creation = fields.String(dump_only=True)
    description = fields.String(required=True)
    date = fields.Date(required=True)
    registration_medium = EnumField(RegistrationMediumEnum, required=True)
    user_id = fields.Int(required=True)
    status = EnumField(StatusEnum, required=True)
    agent_id_last_update = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    client_id = fields.String(dump_only=True)
