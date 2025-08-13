from datetime import datetime

from pydantic import BaseModel, Field


class RescheduledEvent(BaseModel):
    event_id: str = Field(description="The event ID which will be moved. This MUST correspond to an existing event ID.")
    new_start_time: datetime = Field(description="The new start time for the event.")
    new_end_time: datetime = Field(description="The new end time for the event.")
    explanation: str = Field(description="A detailed explanation of the rescheduling proposal.")


class PendingRescheduledEvent(RescheduledEvent):
    pass


class AcceptedRescheduledEvent(RescheduledEvent):
    pass


class RejectedRescheduledEvent(RescheduledEvent):
    pass
