"""Unit tests for MockCalendar class."""

from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest

from src.domains.calendar.mock_calendar import MockCalendar
from src.domains.calendar.mock_events import adams_event, my_first_event, my_second_event, sallys_event
from src.domains.user.mock_user_provider import me, my_user_id, sallys_user, sallys_user_id
from src.types.calendar import CalendarId
from src.types.calendar_event import CalendarEvent, CalendarEventId


@pytest.fixture
def calendar() -> MockCalendar:
    """Create a MockCalendar instance for testing."""
    return MockCalendar(
        id=CalendarId(uuid4()),
        name="Test Calendar",
        owner=my_user_id,
        created_at=datetime.now(tz=ZoneInfo(me.timezone)),
        updated_at=datetime.now(tz=ZoneInfo(me.timezone)),
    )


@pytest.fixture
def calendar_with_events(calendar: MockCalendar):
    """Create a MockCalendar instance with pre-populated events."""
    calendar.add_event(my_first_event)
    calendar.add_event(my_second_event)
    calendar.add_event(adams_event)
    calendar.add_event(sallys_event)


def test_add_event(calendar: MockCalendar):
    """Test adding an event to the calendar."""
    assert len(calendar.events) == 0

    calendar.add_event(my_first_event)
    assert len(calendar.events) == 1
    assert calendar.events[0] == my_first_event

    calendar.add_event(my_second_event)
    assert len(calendar.events) == 2
    assert my_second_event in calendar.events


def test_add_multiple_events(calendar: MockCalendar):
    """Test adding multiple events to the calendar."""
    events = [my_first_event, my_second_event, adams_event, sallys_event]

    for event in events:
        calendar.add_event(event)

    assert len(calendar.events) == 4
    for event in events:
        assert event in calendar.events


def test_get_events_on_same_date(calendar: MockCalendar):
    """Test getting events on the same date."""
    # Add events that are on the same date (2025-08-11)
    calendar.add_event(my_first_event)  # 2025-08-11 09:00-10:00
    calendar.add_event(my_second_event)  # 2025-08-11 13:00-14:00
    calendar.add_event(adams_event)  # 2025-08-11 10:00-12:00

    # Query for the same date
    query_date = datetime(2025, 8, 11, 15, 0, 0, tzinfo=ZoneInfo(me.timezone))
    events = calendar.get_events_on(query_date)

    assert len(events) == 3
    assert my_first_event in events
    assert my_second_event in events
    assert adams_event in events


def test_get_events_on_different_date(calendar: MockCalendar):
    """Test getting events on a different date."""
    # Add events on 2025-08-11
    calendar.add_event(my_first_event)  # 2025-08-11 09:00-10:00
    calendar.add_event(my_second_event)  # 2025-08-11 13:00-14:00

    # Query for a different date
    query_date = datetime(2025, 8, 12, 15, 0, 0, tzinfo=ZoneInfo(me.timezone))
    events = calendar.get_events_on(query_date)

    assert len(events) == 0


def test_get_events_on_empty_calendar(calendar: MockCalendar):
    """Test getting events from an empty calendar."""
    query_date = datetime(2025, 8, 11, 15, 0, 0, tzinfo=ZoneInfo(me.timezone))
    events = calendar.get_events_on(query_date)

    assert len(events) == 0


def test_get_events_on_timezone_handling(calendar: MockCalendar):
    """Test that get_events_on handles timezone differences correctly."""
    # Add an event in one timezone
    calendar.add_event(my_first_event)  # 2025-08-11 09:00-10:00 EST

    # Query with a different timezone but same date
    query_date = datetime(2025, 8, 11, 15, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
    events = calendar.get_events_on(query_date)

    # Should still find the event since we're comparing dates, not times
    assert len(events) == 1
    assert my_first_event in events


@pytest.mark.asyncio
async def test_change_event_time_success(calendar: MockCalendar):
    """Test successfully changing an event's time."""
    calendar.add_event(my_first_event)
    original_updated_at = my_first_event.updated_at

    new_start_time = datetime(2025, 8, 12, 10, 0, 0, tzinfo=ZoneInfo(me.timezone))
    new_end_time = datetime(2025, 8, 12, 11, 0, 0, tzinfo=ZoneInfo(me.timezone))

    await calendar.change_event_time(my_first_event.id, new_start_time, new_end_time)

    # Find the updated event
    updated_event = next(event for event in calendar.events if event.id == my_first_event.id)
    assert updated_event.start_time == new_start_time
    assert updated_event.end_time == new_end_time
    assert updated_event.updated_at is not None
    assert updated_event.updated_at > original_updated_at


@pytest.mark.asyncio
async def test_change_event_time_nonexistent_event(calendar: MockCalendar):
    """Test changing time of a non-existent event raises ValueError."""
    calendar.add_event(my_first_event)

    nonexistent_id = CalendarEventId(999)
    new_start_time = datetime(2025, 8, 12, 10, 0, 0, tzinfo=ZoneInfo(me.timezone))
    new_end_time = datetime(2025, 8, 12, 11, 0, 0, tzinfo=ZoneInfo(me.timezone))

    with pytest.raises(ValueError, match=f"Event with id {nonexistent_id} not found"):
        await calendar.change_event_time(nonexistent_id, new_start_time, new_end_time)


@pytest.mark.asyncio
async def test_change_event_time_empty_calendar(calendar: MockCalendar):
    """Test changing time of an event in an empty calendar raises ValueError."""
    nonexistent_id = CalendarEventId(999)
    new_start_time = datetime(2025, 8, 12, 10, 0, 0, tzinfo=ZoneInfo(me.timezone))
    new_end_time = datetime(2025, 8, 12, 11, 0, 0, tzinfo=ZoneInfo(me.timezone))

    with pytest.raises(ValueError, match=f"Event with id {nonexistent_id} not found"):
        await calendar.change_event_time(nonexistent_id, new_start_time, new_end_time)


@pytest.mark.asyncio
async def test_change_event_time_multiple_events(calendar: MockCalendar):
    """Test changing time of a specific event when multiple events exist."""
    calendar.add_event(my_first_event)
    calendar.add_event(my_second_event)
    calendar.add_event(adams_event)

    # Capture original timestamps
    original_my_first_updated_at = my_first_event.updated_at
    original_my_second_updated_at = my_second_event.updated_at
    original_adams_updated_at = adams_event.updated_at

    new_start_time = datetime(2025, 8, 12, 10, 0, 0, tzinfo=ZoneInfo(me.timezone))
    new_end_time = datetime(2025, 8, 12, 11, 0, 0, tzinfo=ZoneInfo(me.timezone))

    # Change only my_second_event
    await calendar.change_event_time(my_second_event.id, new_start_time, new_end_time)

    # Verify only my_second_event was changed
    for event in calendar.events:
        if event.id == my_second_event.id:
            assert event.start_time == new_start_time
            assert event.end_time == new_end_time
            assert event.updated_at > original_my_second_updated_at
        elif event.id == my_first_event.id:
            # my_first_event should remain unchanged
            assert event.start_time == my_first_event.start_time
            assert event.end_time == my_first_event.end_time
            assert event.updated_at == original_my_first_updated_at
        elif event.id == adams_event.id:
            # adams_event should remain unchanged
            assert event.start_time == adams_event.start_time
            assert event.end_time == adams_event.end_time
            assert event.updated_at == original_adams_updated_at


@pytest.mark.asyncio
async def test_change_event_time_updates_timestamp(calendar: MockCalendar):
    """Test that changing event time updates the updated_at timestamp."""
    calendar.add_event(my_first_event)
    original_updated_at = my_first_event.updated_at

    new_start_time = datetime(2025, 8, 12, 10, 0, 0, tzinfo=ZoneInfo(me.timezone))
    new_end_time = datetime(2025, 8, 12, 11, 0, 0, tzinfo=ZoneInfo(me.timezone))

    await calendar.change_event_time(my_first_event.id, new_start_time, new_end_time)

    updated_event = next(event for event in calendar.events if event.id == my_first_event.id)
    assert updated_event.updated_at > original_updated_at


@pytest.mark.asyncio
async def test_change_event_time_different_owner_timezone():
    """Test that changing event time uses the correct timezone for updated_at."""
    calendar = MockCalendar(
        id=CalendarId(uuid4()),
        name="Test Calendar",
        owner=sallys_user_id,  # Different timezone (America/Los_Angeles)
        created_at=datetime.now(tz=ZoneInfo(sallys_user.timezone)),
        updated_at=datetime.now(tz=ZoneInfo(sallys_user.timezone)),
    )

    # Create an event owned by Sally
    sallys_test_event = CalendarEvent(
        id=CalendarEventId(999),
        title="Sally's Test Event",
        description="Test event for timezone testing",
        owner=sallys_user_id,
        invitees=[],
        start_time=datetime(2025, 8, 11, 10, 0, 0, tzinfo=ZoneInfo(sallys_user.timezone)),
        end_time=datetime(2025, 8, 11, 11, 0, 0, tzinfo=ZoneInfo(sallys_user.timezone)),
        created_at=datetime.now(tz=ZoneInfo(sallys_user.timezone)),
        updated_at=datetime.now(tz=ZoneInfo(sallys_user.timezone)),
    )

    calendar.add_event(sallys_test_event)

    new_start_time = datetime(2025, 8, 12, 10, 0, 0, tzinfo=ZoneInfo(sallys_user.timezone))
    new_end_time = datetime(2025, 8, 12, 11, 0, 0, tzinfo=ZoneInfo(sallys_user.timezone))

    await calendar.change_event_time(sallys_test_event.id, new_start_time, new_end_time)

    updated_event = next(event for event in calendar.events if event.id == sallys_test_event.id)
    # The updated_at should be in Sally's timezone
    assert updated_event.updated_at.tzinfo == ZoneInfo(sallys_user.timezone)
