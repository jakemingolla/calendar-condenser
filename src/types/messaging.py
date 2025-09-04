from abc import ABC
from datetime import datetime

from pydantic import BaseModel

from src.types.messaging_platform import MessagingPlatformId
from src.types.user import User


class BaseMessage(BaseModel, ABC):
    platform_id: MessagingPlatformId
    content: str
    sent_at: datetime
    from_user: User
    to_user: User


class OutgoingMessage(BaseMessage):
    """A message sent by the user."""


class IncomingMessage(BaseMessage):
    """A message received from another user."""


class Conversation(BaseModel):
    messages: list[OutgoingMessage | IncomingMessage]
