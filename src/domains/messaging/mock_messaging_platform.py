from datetime import UTC, datetime, timedelta
from random import choice, randint, random
from typing import override
from uuid import uuid4
from zoneinfo import ZoneInfo

from pydantic import Field

from src.config.main import config
from src.types.messaging_platform import MessageReceipt, MessageReceiptNotFoundError, MessagingPlatform, MessagingPlatformId
from src.types.user import User


def get_unlock_time() -> datetime:
    delay = randint(
        config.mock_messaging_platform_unlock_time_min_seconds,
        config.mock_messaging_platform_unlock_time_max_seconds,
    )
    return datetime.now(ZoneInfo("America/New_York")) + timedelta(seconds=delay)


def get_positive_response() -> str:
    return choice(
        [
            "Sure, I can do that.",
            "Sounds good.",
            "Yep.",
            "I'll do it.",
            "Works for me.",
            "👍",
        ],
    )


def get_negative_response() -> str:
    return choice(
        [
            "Sorry, I can't do that.",
            "I'm sorry, I can't do that.",
            "Nope",
            "no",
            "Sorry, I'm busy then.",
            "👎",
        ],
    )


class MockMessagingPlatform(MessagingPlatform):
    id: MessagingPlatformId = "slack"
    message_receipt_created_at: dict[MessageReceipt, datetime] = Field(default_factory=dict)
    message_receipt_unlocks_at: dict[MessageReceipt, datetime] = Field(default_factory=dict)
    message_responses: dict[MessageReceipt, str] = Field(default_factory=dict)

    @override
    async def send_message(self, user: User, message: str) -> MessageReceipt:
        receipt = MessageReceipt(uuid4())
        self.message_receipt_created_at[receipt] = datetime.now(ZoneInfo("America/New_York"))
        self.message_receipt_unlocks_at[receipt] = get_unlock_time()
        return receipt

    @override
    async def get_message_response(self, receipt: MessageReceipt) -> str | None:
        unlocks_at = self.message_receipt_unlocks_at.get(receipt)

        if unlocks_at is None:
            raise MessageReceiptNotFoundError(receipt)

        if unlocks_at > datetime.now(tz=UTC):
            return None

        if receipt not in self.message_responses:
            if random() <= config.mock_messaging_platform_positive_response_probability:
                self.message_responses[receipt] = get_positive_response()
            else:
                self.message_responses[receipt] = get_negative_response()

        return self.message_responses[receipt]
