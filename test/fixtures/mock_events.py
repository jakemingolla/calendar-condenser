from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from src.types.calendar_event import CalendarEvent, CalendarEventId
from src.types.user import UserId


@pytest.fixture
def mock_event() -> CalendarEvent:
    return CalendarEvent(
        id=CalendarEventId(1),
        title="Test Event",
        description="Test Description",
        owner=UserId(uuid4()),
        invitees=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1),
    )
