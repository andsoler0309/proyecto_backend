from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class SecurityAnswerSchema(Schema):
    verification_id = fields.Str(required=True)
    answer = fields.Str(required=True)


class VerificationSchema(Schema):
    verification_id = fields.Str(dump_only=True)
    agent_id = fields.Str(required=True)
    security_question = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)


class AgentCreationSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    password = fields.Str(
        required=True, load_only=True, validate=validate.Length(min=6)
    )
    role = fields.Str(required=True, validate=validate.OneOf(["agent", "admin"]))
    identification = fields.Str(required=True)
    phone = fields.Str(required=True)
    address = fields.Str(required=True)
    city = fields.Str(required=True)
    state = fields.Str(required=True)
    zip_code = fields.Str(required=True)
    country = fields.Str(required=True)


class IncidentCreationSchema(Schema):
    agent_id = fields.Str(required=True, load_only=True)
    agent_id_creation = fields.Str(dump_only=True)
    description = fields.Str(required=True, validate=validate.Length(min=1))
    date = fields.Date(required=True)
    registration_medium = fields.Str(required=True)
    user_id = fields.Int(required=True)
    status = fields.Str(dump_only=True)
    agent_id_last_update = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    client_id = fields.Str(required=True)


class IncidentUpdateSchema(Schema):
    agent_id = fields.Str(required=True, load_only=True)
    agent_id_creation = fields.Str(dump_only=True)
    description = fields.Str(required=True, validate=validate.Length(min=1))
    date = fields.Date(required=True)
    registration_medium = fields.Str(required=True)
    user_id = fields.Int(required=True)
    status = fields.Str(required=True)
    agent_id_last_update = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    client_id = fields.Str(dump_only=True)


class AdminActionSchema(Schema):
    agent_id = fields.Str(required=True)


class ClientCreationSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(
        required=True, load_only=True, validate=validate.Length(min=6)
    )
    name = fields.Str(required=True, validate=validate.Length(min=1))
    company_name = fields.Str(required=True, validate=validate.Length(min=1))


class PlanSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True)
    descripcion = fields.Str(required=True)


class ClientSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    company_name = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    plan_id = fields.Str(required=True)
    plan = fields.Nested(PlanSchema, dump_only=True)


class ClientPlanSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    company_name = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    plan_id = fields.Str(required=True)
    plan = fields.Nested(PlanSchema, dump_only=True)


class ChatBotSchema(Schema):
    message = fields.Str(required=True)
    chatbot_conversation_id = fields.Str(required=False)