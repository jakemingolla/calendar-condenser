"""Unit tests for MockMessagingPlatform class."""

import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

import pytest

from src.domains.messaging.mock_messaging_platform import MockMessagingPlatform
from src.domains.user.mock_user_provider import adams_user, me, sallys_user
from src.types.messaging_platform import MessageReceipt, MessageReceiptNotFoundError


@pytest.fixture
def messaging_platform() -> MockMessagingPlatform:
    """Create a MockMessagingPlatform instance for testing."""
    return MockMessagingPlatform()


@pytest.fixture
def sample_message() -> str:
    """Create a sample message for testing."""
    return "Hello! Can we reschedule our meeting to tomorrow at 2 PM?"


@pytest.fixture
def different_message() -> str:
    """Create a different sample message for testing."""
    return "Thanks for the update. See you then!"


def test_messaging_platform_id(messaging_platform: MockMessagingPlatform):
    """Test that the messaging platform has the correct ID."""
    assert messaging_platform.id == "slack"


@pytest.mark.asyncio
async def test_send_message_returns_receipt(messaging_platform: MockMessagingPlatform, sample_message: str):
    """Test that send_message returns a valid MessageReceipt."""
    receipt = await messaging_platform.send_message(me, sample_message)

    assert isinstance(receipt, UUID)
    assert receipt is not None


@pytest.mark.asyncio
async def test_send_message_unique_receipts(messaging_platform: MockMessagingPlatform, sample_message: str):
    """Test that send_message returns unique receipts for different calls."""
    receipt1 = await messaging_platform.send_message(me, sample_message)
    receipt2 = await messaging_platform.send_message(me, sample_message)

    assert receipt1 != receipt2


@pytest.mark.asyncio
async def test_send_message_different_users(messaging_platform: MockMessagingPlatform, sample_message: str):
    """Test that send_message works with different users."""
    receipt1 = await messaging_platform.send_message(me, sample_message)
    receipt2 = await messaging_platform.send_message(adams_user, sample_message)
    receipt3 = await messaging_platform.send_message(sallys_user, sample_message)

    assert receipt1 != receipt2
    assert receipt2 != receipt3
    assert receipt1 != receipt3


@pytest.mark.asyncio
async def test_send_message_different_messages(messaging_platform: MockMessagingPlatform):
    """Test that send_message works with different message content."""
    message1 = "Hello, how are you?"
    message2 = "Can we meet tomorrow?"
    message3 = "Thanks for your time!"

    receipt1 = await messaging_platform.send_message(me, message1)
    receipt2 = await messaging_platform.send_message(me, message2)
    receipt3 = await messaging_platform.send_message(me, message3)

    assert receipt1 != receipt2
    assert receipt2 != receipt3
    assert receipt1 != receipt3


@pytest.mark.asyncio
async def test_send_message_sets_timing_data(messaging_platform: MockMessagingPlatform, sample_message: str):
    """Test that send_message sets up timing data for the receipt."""
    before_send = datetime.now(ZoneInfo("America/New_York"))
    receipt = await messaging_platform.send_message(me, sample_message)
    after_send = datetime.now(ZoneInfo("America/New_York"))

    # Check that timing data was set
    assert receipt in messaging_platform.message_receipt_created_at
    assert receipt in messaging_platform.message_receipt_unlocks_at

    # Check that created_at is within reasonable bounds
    created_at = messaging_platform.message_receipt_created_at[receipt]
    assert before_send <= created_at <= after_send

    # Check that unlock time is in the future (2-5 seconds from now)
    unlock_time = messaging_platform.message_receipt_unlocks_at[receipt]
    assert unlock_time > created_at
    assert unlock_time <= created_at + timedelta(seconds=5)


@pytest.mark.asyncio
async def test_get_message_response_before_unlock_returns_none(messaging_platform: MockMessagingPlatform, sample_message: str):
    """Test that get_message_response returns None before the unlock time."""
    receipt = await messaging_platform.send_message(me, sample_message)

    # Should return None immediately after sending
    response = await messaging_platform.get_message_response(receipt)
    assert response is None


@pytest.mark.asyncio
async def test_get_message_response_after_unlock_returns_response(messaging_platform: MockMessagingPlatform, sample_message: str):
    """Test that get_message_response returns a response after the unlock time."""
    receipt = await messaging_platform.send_message(me, sample_message)

    # Manually set unlock time to the past
    messaging_platform.message_receipt_unlocks_at[receipt] = datetime.now(UTC) - timedelta(seconds=1)

    response = await messaging_platform.get_message_response(receipt)
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
async def test_get_message_response_consistent_response(messaging_platform: MockMessagingPlatform, sample_message: str):
    """Test that get_message_response returns the same response for the same receipt."""
    receipt = await messaging_platform.send_message(me, sample_message)

    # Manually set unlock time to the past
    messaging_platform.message_receipt_unlocks_at[receipt] = datetime.now(UTC) - timedelta(seconds=1)

    # Get response multiple times
    response1 = await messaging_platform.get_message_response(receipt)
    response2 = await messaging_platform.get_message_response(receipt)
    response3 = await messaging_platform.get_message_response(receipt)

    assert response1 == response2 == response3
    assert response1 is not None


@pytest.mark.asyncio
async def test_get_message_response_nonexistent_receipt_raises_error(messaging_platform: MockMessagingPlatform):
    """Test that get_message_response raises MessageReceiptNotFoundError for nonexistent receipt."""
    nonexistent_receipt = MessageReceipt(uuid4())

    with pytest.raises(MessageReceiptNotFoundError) as exc_info:
        await messaging_platform.get_message_response(nonexistent_receipt)

    assert exc_info.value.receipt == nonexistent_receipt


@pytest.mark.asyncio
async def test_send_message_with_empty_string(messaging_platform: MockMessagingPlatform):
    """Test that send_message works with empty string message."""
    receipt = await messaging_platform.send_message(me, "")

    assert isinstance(receipt, UUID)
    assert receipt is not None


@pytest.mark.asyncio
async def test_send_message_with_very_long_message(messaging_platform: MockMessagingPlatform):
    """Test that send_message works with very long message."""
    long_message = "This is a very long message. " * 1000  # ~30KB message
    receipt = await messaging_platform.send_message(me, long_message)

    assert isinstance(receipt, UUID)
    assert receipt is not None


@pytest.mark.asyncio
async def test_send_message_with_special_characters(messaging_platform: MockMessagingPlatform):
    """Test that send_message works with special characters and unicode."""
    special_message = "Hello! 👋 Can we meet at 2:30 PM? 🕐 Thanks! 😊"
    receipt = await messaging_platform.send_message(me, special_message)

    assert isinstance(receipt, UUID)
    assert receipt is not None


@pytest.mark.asyncio
async def test_concurrent_send_messages(messaging_platform: MockMessagingPlatform):
    """Test sending multiple messages concurrently."""
    messages = [
        "Message 1",
        "Message 2",
        "Message 3",
        "Message 4",
        "Message 5",
    ]

    # Send all messages concurrently
    tasks = [messaging_platform.send_message(me, message) for message in messages]
    receipts = await asyncio.gather(*tasks)

    # All receipts should be unique
    assert len(set(receipts)) == len(receipts)

    # All should be valid MessageReceipts
    for receipt in receipts:
        assert isinstance(receipt, UUID)


@pytest.mark.asyncio
async def test_concurrent_get_responses(messaging_platform: MockMessagingPlatform):
    """Test getting responses for multiple messages concurrently."""
    # Send multiple messages
    receipts: list[MessageReceipt] = []
    for i in range(5):
        receipt = await messaging_platform.send_message(me, f"Message {i}")
        receipts.append(receipt)
        # Set unlock time to past
        messaging_platform.message_receipt_unlocks_at[receipt] = datetime.now(UTC) - timedelta(seconds=1)

    # Get all responses concurrently
    tasks = [messaging_platform.get_message_response(receipt) for receipt in receipts]
    responses = await asyncio.gather(*tasks)

    # All should have responses
    for response in responses:
        assert response is not None
        assert isinstance(response, str)


@pytest.mark.asyncio
async def test_mixed_user_messages(messaging_platform: MockMessagingPlatform):
    """Test sending messages to different users and getting their responses."""
    users = [me, adams_user, sallys_user]
    messages = ["Hello from me", "Hello from Adam", "Hello from Sally"]

    # Send messages to different users
    receipts: list[MessageReceipt] = []
    for user, message in zip(users, messages, strict=False):
        receipt = await messaging_platform.send_message(user, message)
        receipts.append(receipt)
        # Set unlock time to past
        messaging_platform.message_receipt_unlocks_at[receipt] = datetime.now(UTC) - timedelta(seconds=1)

    # Get responses
    responses = []
    for receipt in receipts:
        response = await messaging_platform.get_message_response(receipt)
        responses.append(response)

    # All should have responses
    for response in responses:
        assert response is not None
        assert isinstance(response, str)
