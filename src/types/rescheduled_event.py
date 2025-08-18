from datetime import datetime

from pydantic import BaseModel, Field

from src.types.calendar_event import CalendarEvent


class RescheduledEvent(BaseModel):
    original_event: CalendarEvent = Field(description="The event pending rescheduling.")
    new_start_time: datetime = Field(description="The new start time for the event.")
    new_end_time: datetime = Field(description="The new end time for the event.")
    explanation: str = Field(description="A detailed explanation of the rescheduling proposal.")


class PendingRescheduledEvent(RescheduledEvent):
    pass


class AcceptedRescheduledEvent(RescheduledEvent):
    pass


class RejectedRescheduledEvent(RescheduledEvent):
    pass
