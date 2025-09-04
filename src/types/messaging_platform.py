from abc import ABC, abstractmethod
from typing import Literal, NewType, Self
from uuid import UUID

from pydantic import BaseModel

from src.types.user import User

MessageReceipt = NewType("MessageReceipt", UUID)
MessagingPlatformId = Literal["slack", "microsoft-teams"]


class MessageReceiptNotFoundError(Exception):
    def __init__(self: Self, receipt: MessageReceipt) -> None:
        """Initialize the error with the receipt that was not found."""
        self.receipt = receipt
        super().__init__(f"Message receipt {receipt} not found")


class MessagingPlatform(ABC, BaseModel):
    id: MessagingPlatformId

    @abstractmethod
    async def send_message(self: Self, user: User, message: str) -> MessageReceipt:
        """Send a message to a user.

        Args:
            user: The user to send the message to.
            message: The message to send.

        Returns:
            The receipt of the message.

        """
        raise NotImplementedError

    # TODO: Handle emoji reactions
    @abstractmethod
    async def get_message_response(self: Self, receipt: MessageReceipt) -> str | None:
        """Get the user's response to a message.

        Args:
            receipt: The receipt of the message to get.

        Returns:
            The message, or None if the message is not found.

        """
        raise NotImplementedError
