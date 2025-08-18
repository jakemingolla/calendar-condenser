from abc import ABC
from datetime import datetime

from pydantic import Field

from src.types.calendar_event import CalendarEvent
from src.types.higher_order import BrandedBaseModel


class RescheduledEvent(BrandedBaseModel, ABC):
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
