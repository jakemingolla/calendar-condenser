from collections.abc import Sequence
from datetime import datetime
from typing import Literal, Self

from src.domains.google_calendar.types.google_calendar_event import GoogleCalendarEvent
from src.types.calendar import Calendar


class GoogleCalendar(Calendar):
    type: Literal["google_calendar"] = "google_calendar"

    def get_events_on(self: Self, date: datetime) -> Sequence[GoogleCalendarEvent]:  # noqa: ARG002
        """Get all events on the given date.

        Args:
            date: The date to get events for.

        Returns:
            A list of events on the given date.

        """
        # TODO this will be implemented later, return empty list for now
        return []
