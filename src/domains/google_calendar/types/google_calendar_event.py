from typing import Literal

from src.types.calendar_event import CalendarEvent


class GoogleCalendarEvent(CalendarEvent):
    type: Literal["google_calendar_event"] = "google_calendar_event"
