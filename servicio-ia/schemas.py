from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from enum import Enum
from models import ChatbotState, ChatbotConversation


class ChatbotConversationSchema(Schema):
    id = fields.String(dump_only=True)
    user_id = fields.String(required=False)
    state = EnumField(ChatbotState, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    client_id = fields.String(required=False)
    incident_description = fields.String(required=False)
