from marshmallow import Schema, fields


class IncidentSchema(Schema):
    id = fields.String(dump_only=True)
    agent_id = fields.String(required=True)
    description = fields.String(required=True)
    date = fields.Date(required=True)
