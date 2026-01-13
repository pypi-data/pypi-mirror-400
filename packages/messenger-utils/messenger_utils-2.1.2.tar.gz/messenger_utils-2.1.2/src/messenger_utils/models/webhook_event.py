"""
Webhook Events Classes
"""

__all__ = [
    "EventTypes", "AttachmentTypes", "Attachment", "WebhookEvent", "MessageCreatedEvent", "MessageCallbackEvent", "WebhookEventType"
]


from typing import Literal
from dataclasses import dataclass, field



EventTypes = Literal[
    "bot_started",
    "bot_stopped",
    "dialog_cleared",
    "dialog_removed",
    "message_created",
    "message_callback"
]


AttachmentTypes = Literal[
    "image",
    "audio"
]


@dataclass
class Attachment:
    """
    Image attachment type.
    """
    attachment_type: AttachmentTypes
    url: str
    token: str


@dataclass(slots=True)
class WebhookEvent:
    """
    Base class for all webhook events.
    """
    event_type: EventTypes
    chat_id: int
    user_id: int
    user_name: str          # ["user"]["name"] of request body
    user_is_bot: bool
    timestamp: int
    full_body: dict         # JSON body of original webjook request


@dataclass(slots=True)
class MessageCreatedEvent(WebhookEvent):
    """
    Event whith type `message_created`.
    """
    text: str
    recipient_id: int
    attachments: list[Attachment] = field(default_factory=list[Attachment])


@dataclass(slots=True)
class MessageCallbackEvent(WebhookEvent):
    """
    Event of callback from keyboard button
    """
    callback_id: str
    payload: str        # Button token


WebhookEventType = WebhookEvent | MessageCreatedEvent | MessageCallbackEvent
