from collections.abc import Sequence
from datetime import datetime
from typing import Literal, Self, override

from pydantic import Field

from src.domains.google_calendar.types.google_calendar_event import (
    GoogleCalendarEvent,
)
from src.types.calendar import Calendar
from src.types.calendar_event import CalendarEventId


class GoogleCalendar(Calendar):
    type: Literal["google_calendar"] = "google_calendar"
    events: list[GoogleCalendarEvent] = Field(default_factory=list)

    def add_event(self: Self, event: GoogleCalendarEvent) -> None:
        """Add an event to the calendar.

        Args:
            event: The event to add.

        """
        self.events.append(event)

    def remove_event(self: Self, event_id: CalendarEventId) -> None:
        """Remove an event from the calendar.

        Args:
            event_id: The ID of the event to remove.

        """
        self.events = [event for event in self.events if event.id != event_id]

    @override
    def get_events_on(self: Self, date: datetime) -> Sequence[GoogleCalendarEvent]:
        """Get all events on the given date.

        Args:
            date: The date to get events for.

        Returns:
            A list of events on the given date.

        """
        # TODO this will be implemented later, return empty list for now
        return [event for event in self.events if event.start_time.date() == date.date()]
