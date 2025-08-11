import asyncio
from collections.abc import Sequence
from datetime import datetime
from zoneinfo import ZoneInfo

from langgraph.graph import END, START, StateGraph
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
from src.types.calendar_event import CalendarEvent
from src.types.user import User, UserId


class State(BaseModel):
    user: User
    events_for_today_by_user_id: dict[UserId, Sequence[CalendarEvent]] = Field(default_factory=dict)


def get_events_for_today(state: State) -> State:
    state.events_for_today_by_user_id[state.user.id] = my_calendar.get_events_on(
        datetime.now(tz=ZoneInfo(me.timezone)),
    )
    return state


def get_events_for_invitees(state: State) -> State:
    # Process all events for today and get events for their invitees
    for event in state.events_for_today_by_user_id[state.user.id]:
        for invitee in event.invitees:
            if invitee.id not in state.events_for_today_by_user_id:
                if invitee.id == adams_user_id:
                    state.events_for_today_by_user_id[invitee.id] = adams_calendar.get_events_on(
                        datetime.now(tz=ZoneInfo(adams_user.timezone)),
                    )
                elif invitee.id == sallys_user_id:
                    state.events_for_today_by_user_id[invitee.id] = sallys_calendar.get_events_on(
                        datetime.now(tz=ZoneInfo(sallys_user.timezone)),
                    )
    return state


async def get_rescheduling_proposals(state: State) -> State:
    events = state.events_for_today_by_user_id[state.user.id]
    invitees_and_their_events = [
        (other_user_id, other_events)
        for other_user_id, other_events in state.events_for_today_by_user_id.items()
        if other_user_id != state.user.id
    ]
    rescheduling_proposal = await generate_rescheduling_proposal(state.user, events, invitees_and_their_events)
    print("Rescheduling proposal")
    print("Event ID:", str(rescheduling_proposal.event_id)[:8])
    print("New start time:", rescheduling_proposal.new_start_time.hour)
    print("New end time:", rescheduling_proposal.new_end_time.hour)
    print("Explanation:", rescheduling_proposal.explanation)
    return state


def print_state(state: State) -> State:
    for user_id, events in state.events_for_today_by_user_id.items():
        print()
        print(f"User {str(user_id)[:8]}:")
        for event in events:
            print(f"  {str(event.id)[:8]} from {event.start_time.hour} to {event.end_time.hour}")
    return state


graph = StateGraph(State)

graph.add_node("get_events_for_today", get_events_for_today)
graph.add_node("get_events_for_invitees", get_events_for_invitees)
graph.add_node("get_rescheduling_proposals", get_rescheduling_proposals)
graph.add_node("print_state", print_state)

graph.add_edge(START, "get_events_for_today")
graph.add_edge("get_events_for_today", "get_events_for_invitees")
graph.add_edge("get_events_for_invitees", "get_rescheduling_proposals")
graph.add_edge("get_rescheduling_proposals", "print_state")
graph.add_edge("print_state", END)


compiled_graph = graph.compile()


async def main() -> None:
    state = State(user=me)
    await compiled_graph.ainvoke(state)


if __name__ == "__main__":
    asyncio.run(main())

# state:
# - events_for_today_by_user_id: dict[UserId, list[CalendarEvent]]
#
#
# 1. Load user's calendar
# 2. Get events for today
# 3. For each event:
#       - Load the calendar for each invitee
# 4. Generate proposed changes to start/end times for each event
# 5. Group each proposed change by user_id
# 6. For each user_id with proposed changes:
# 7.    - Send message to user_id with proposed changes
# 8. For each user_id with proposed changes:
# 9.    - Periodically check for confirmation
# -- TODO: Handle failures --
