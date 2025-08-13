import asyncio
from collections.abc import Sequence
from datetime import datetime
from zoneinfo import ZoneInfo

from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from src.agents.rescheduling import generate_rescheduling_proposal
from src.graph.mock_data import (
    adams_calendar,
    adams_user,
    adams_user_id,
    me,
    my_calendar,
    sallys_calendar,
    sallys_user,
    sallys_user_id,
)
from src.types.calendar import Calendar
from src.types.user import User, UserId


class InitialState(BaseModel):
    user: User


class StateWithCalendar(InitialState):
    calendar: Calendar


class StateWithInvitees(StateWithCalendar):
    invitees: Sequence[User]
    invitee_calendars: dict[UserId, Calendar] = Field(default_factory=dict)


def load_calendar(state: InitialState) -> StateWithCalendar:
    return StateWithCalendar(user=state.user, calendar=my_calendar)


def load_invitees(state: StateWithCalendar) -> StateWithInvitees:
    return StateWithInvitees(
        user=state.user,
        calendar=state.calendar,
        invitees=[adams_user, sallys_user],
        invitee_calendars={adams_user_id: adams_calendar, sallys_user_id: sallys_calendar},
    )


async def get_rescheduling_proposals(state: StateWithInvitees) -> StateWithInvitees:
    date = datetime(2025, 8, 11, tzinfo=ZoneInfo(me.timezone))
    other_invitees = [(adams_user, adams_calendar), (sallys_user, sallys_calendar)]
    rescheduling_proposal = await generate_rescheduling_proposal(date, me, my_calendar, other_invitees)

    print("Rescheduling proposals:")
    for event in rescheduling_proposal:
        print("Event ID:", str(event.event_id)[:8])
        print("New start time:", event.new_start_time.hour)
        print("New end time:", event.new_end_time.hour)
        print("Explanation:", event.explanation)
    return state


graph = StateGraph(InitialState)

# Set the entry point state type
graph.set_entry_point("load_calendar")

graph.add_node("load_calendar", load_calendar)
graph.add_node("load_invitees", load_invitees)
graph.add_node("get_rescheduling_proposals", get_rescheduling_proposals)

graph.add_edge("load_calendar", "load_invitees")
graph.add_edge("load_invitees", "get_rescheduling_proposals")
graph.add_edge("get_rescheduling_proposals", END)


compiled_graph = graph.compile()


async def main() -> None:
    initial_state = InitialState(user=me)
    await compiled_graph.ainvoke(initial_state)


if __name__ == "__main__":
    asyncio.run(main())
