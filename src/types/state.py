from collections.abc import Sequence
from datetime import datetime
from typing import Annotated, Any, Self, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from src.types.calendar import Calendar
from src.types.messaging import IncomingMessage, OutgoingMessage
from src.types.rescheduled_event import AcceptedRescheduledEvent, PendingRescheduledEvent, RejectedRescheduledEvent
from src.types.user import User, UserId

K = TypeVar("K")
V = TypeVar("V")


def merge_dicts(dict1: dict[K, V], dict2: dict[K, V]) -> dict[K, V]:
    """Merge two dictionaries, with dict2 values taking precedence."""
    return {**dict1, **dict2}


class State(BaseModel):
    # Because the `from_previous_state` method has `kwargs` typed as `Any`, we can't check for extra
    # fields during type checking. This makes sure we don't leave behind any extra fields (done at runtime).
    model_config = ConfigDict(extra="forbid")

    @classmethod
    def from_previous_state(cls: type[Self], previous_state: BaseModel, **kwargs: Any) -> Self:  # noqa: ANN401
        """Return a new instance of the new state class using the previous state and the new kwargs.

        Params:
            previous_state: The previous state.
            kwargs: The new kwargs to update the state with.

        Returns:
            A new instance of the new state class using the previous state and the new kwargs.

        """
        return cls.model_validate(dict(previous_state, **kwargs))

    type: str = ""  # NOTE: Overridden in `model_post_init`

    def model_post_init(self, __context: Any, /) -> None:  # noqa: ANN401
        """Set the type field to the actual class name after initialization."""
        object.__setattr__(self, "type", self.__class__.__name__)


class InitialState(State):
    user: User
    date: datetime


class StateWithCalendar(InitialState):
    calendar: Calendar


class StateWithInvitees(StateWithCalendar):
    invitees: Sequence[User]
    invitee_calendars: dict[UserId, Calendar] = Field(default_factory=dict)


class StateWithPendingReschedulingProposals(StateWithInvitees):
    # TODO This needs to be able to handle multiple proposals for different events.
    pending_rescheduling_proposals: list[PendingRescheduledEvent]


class StateWithInviteeMessages(StateWithPendingReschedulingProposals):
    conversations_by_invitee: Annotated[dict[UserId, list[IncomingMessage | OutgoingMessage]], merge_dicts]


class StateWithCompletedReschedulingProposals(StateWithInviteeMessages):
    completed_rescheduling_proposals: list[AcceptedRescheduledEvent | RejectedRescheduledEvent]
