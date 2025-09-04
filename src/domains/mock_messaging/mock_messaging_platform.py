from datetime import datetime, timedelta
from random import choice, randint
from typing import override
from uuid import uuid4
from zoneinfo import ZoneInfo

from src.types.messaging_platform import MessageReceipt, MessageReceiptNotFoundError, MessagingPlatform, MessagingPlatformId
from src.types.user import User

message_receipt_created_at: dict[MessageReceipt, datetime] = {}
message_receipt_unlocks_at: dict[MessageReceipt, datetime] = {}
message_responses: dict[MessageReceipt, str] = {}


def get_unlock_time() -> datetime:
    delay = randint(2, 5)
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

    @override
    async def send_message(self, user: User, message: str) -> MessageReceipt:
        receipt = MessageReceipt(uuid4())
        message_receipt_created_at[receipt] = datetime.now(ZoneInfo("America/New_York"))
        message_receipt_unlocks_at[receipt] = get_unlock_time()
        return receipt

    @override
    async def get_message_response(self, receipt: MessageReceipt) -> str | None:
        unlocks_at = message_receipt_unlocks_at.get(receipt)

        if unlocks_at is None:
            raise MessageReceiptNotFoundError(receipt)

        if unlocks_at > datetime.now(ZoneInfo("America/New_York")):
            return None

        if receipt not in message_responses:
            if choice([True, False]):
                message_responses[receipt] = get_positive_response()
            else:
                message_responses[receipt] = get_negative_response()

        return message_responses[receipt]
