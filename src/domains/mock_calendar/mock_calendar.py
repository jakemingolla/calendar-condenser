from datetime import datetime
from typing import Self, override
from uuid import uuid4
from zoneinfo import ZoneInfo

from pydantic import Field

from src.domains.mock_calendar.mock_events import adams_event, my_first_event, my_second_event, sallys_event
from src.domains.mock_user.mock_user_provider import (
    adams_user,
    adams_user_id,
    me,
    mock_users,
    my_user_id,
    sallys_user,
    sallys_user_id,
)
from src.types.calendar import Calendar, CalendarId
from src.types.calendar_event import CalendarEvent, CalendarEventId


class MockCalendar(Calendar):
    events: list[CalendarEvent] = Field(default_factory=list)

    def add_event(self: Self, event: CalendarEvent) -> None:
        """Add an event to the calendar."""
        self.events.append(event)

    @override
    def get_events_on(self: Self, date: datetime) -> list[CalendarEvent]:
        return [event for event in self.events if event.start_time.date() == date.date()]

    @override
    async def change_event_time(self: Self, event_id: CalendarEventId, new_start_time: datetime, new_end_time: datetime) -> None:
        for event in self.events:
            if event.id == event_id:
                event.start_time = new_start_time
                event.end_time = new_end_time
                event.updated_at = datetime.now(tz=ZoneInfo(mock_users[event.owner].timezone))
                return
        msg = f"Event with id {event_id} not found"
        raise ValueError(msg)


my_calendar = MockCalendar(
    id=CalendarId(uuid4()),
    name="My Calendar",
    owner=my_user_id,
    created_at=datetime.now(tz=ZoneInfo(me.timezone)),
    updated_at=datetime.now(tz=ZoneInfo(me.timezone)),
)

my_calendar.add_event(my_first_event)
my_calendar.add_event(my_second_event)

adams_calendar = MockCalendar(
    id=CalendarId(uuid4()),
    name="Adam's Calendar",
    owner=adams_user_id,
    created_at=datetime.now(tz=ZoneInfo(adams_user.timezone)),
    updated_at=datetime.now(tz=ZoneInfo(adams_user.timezone)),
)

adams_calendar.add_event(adams_event)
adams_calendar.add_event(my_first_event)
adams_calendar.add_event(my_second_event)

sallys_calendar = MockCalendar(
    id=CalendarId(uuid4()),
    name="Sally's Calendar",
    owner=sallys_user_id,
    events=[],
    created_at=datetime.now(tz=ZoneInfo(sallys_user.timezone)),
    updated_at=datetime.now(tz=ZoneInfo(sallys_user.timezone)),
)

sallys_calendar.add_event(my_first_event)
sallys_calendar.add_event(my_second_event)
sallys_calendar.add_event(sallys_event)
