"""
MAX messenger inits.
"""
MAX_API_URL = "https://platform-api.max.ru"

from .. import logger
from .max_sender import MaxSender
from .max_receiver import MaxReceiver
from .max_keyboard import MaxKeyboard, CallbackButton
from ..models.webhook_event import WebhookEventType, WebhookEvent, MessageCreatedEvent, MessageCallbackEvent, EventTypes


__all__ = [
    "logger",
    "MAX_API_URL",
    "MaxSender",
    "MaxReceiver",
    "MaxKeyboard",
    "CallbackButton",
    "WebhookEvent",
    "WebhookEventType",
    "MessageCreatedEvent",
    "MessageCallbackEvent",
    "EventTypes"
]
