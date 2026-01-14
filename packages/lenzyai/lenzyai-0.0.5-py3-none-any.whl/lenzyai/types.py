from typing import Dict, List, Optional, TypedDict, Union
from typing_extensions import Literal
from datetime import datetime


class MessageRole:
    USER = "USER"
    ASSISTANT = "ASSISTANT"


MessageRoleType = Literal["USER", "ASSISTANT"]


class Message(TypedDict, total=False):
    role: MessageRoleType
    content: str
    external_id: str
    sent_at: str


class AlertEvent(TypedDict, total=False):
    id: str
    description: str
    reason: str
    user_quote: str
    user_message_id: str
    external_user_message_id: str
    assistant_quote: str
    assistant_message_id: str
    external_assistant_message_id: str
    user_id: str
    external_user_id: str
    happened_at: str
    fields: Dict[str, str]
    last_happened_for_user_at: str


class AlertWebhookData(TypedDict):
    alert_id: str
    events: List[AlertEvent]


class AlertWebhookEvent(TypedDict):
    type: Literal["alert"]
    data: AlertWebhookData

WebhookEvent = Union[AlertWebhookEvent]
