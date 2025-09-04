from abc import ABC
from datetime import datetime

from pydantic import BaseModel

from src.types.user import User


class BaseMessage(BaseModel, ABC):
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
