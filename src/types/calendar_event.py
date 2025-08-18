from abc import ABC
from datetime import datetime
from typing import Literal, NewType, Self
from uuid import UUID

from pydantic import Field

from src.types.higher_order import BrandedBaseModel
from src.types.user import UserId

CalendarEventId = NewType("CalendarEventId", UUID)


class CalendarEventInvitee(BrandedBaseModel):
    id: UserId
    confirmed: bool | None = None
    confirmed_at: datetime | None = None


class CalendarEvent(BrandedBaseModel, ABC):
    id: CalendarEventId
    title: str
    description: str | None = None
    owner: UserId
    invitees: list[CalendarEventInvitee] = Field(default_factory=list)
    start_time: datetime
    end_time: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    def duration(
        self: Self,
        unit: Literal["seconds", "minutes", "hours", "days"] = "minutes",
        precision: int = 2,
    ) -> float:
        """Get the duration of the event in the given unit.

        Args:
            unit: The unit to return the duration in.
            precision: The number of decimal places to round the duration to.

        Returns:
            The duration of the event in the given unit.

        """
        duration = (self.end_time - self.start_time).total_seconds() / {
            "seconds": 1,
            "minutes": 60,
            "hours": 3600,
            "days": 86400,
        }[unit]
        return round(duration, precision)
