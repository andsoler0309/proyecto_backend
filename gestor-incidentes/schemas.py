from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from enum import Enum
from models import RegistrationMediumEnum, StatusEnum


class IncidentSchema(Schema):
    id = fields.String(dump_only=True)
    agent_id_creation = fields.String(required=True)
    description = fields.String(required=True)
    date = fields.Date(required=True)
    registration_medium = EnumField(RegistrationMediumEnum, required=True)
    user_id = fields.String(required=True)
    status = EnumField(StatusEnum, dump_only=True)
    agent_id_last_update = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
