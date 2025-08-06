from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime
from typing import NewType, Self
from uuid import UUID

from pydantic import BaseModel

from src.types.calendar_event import CalendarEvent
from src.types.user import UserId

CalendarId = NewType("CalendarId", UUID)


class Calendar(BaseModel, ABC):
    id: CalendarId
    name: str
    owner: UserId
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @abstractmethod
    def get_events_on(self: Self, date: datetime) -> Sequence[CalendarEvent]:
        """Get all events on the given date.

        Args:
            date: The date to get events for.

        Returns:
            A list of events on the given date.

        """
