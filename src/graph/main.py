import asyncio
from collections.abc import Sequence
from datetime import datetime
from zoneinfo import ZoneInfo

from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from src.agents.messaging import submit_rescheduling_proposal

# from src.agents.rescheduling import generate_rescheduling_proposals
from src.agents.summary import summarize_rescheduling_proposals
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
from src.types.rescheduled_event import AcceptedRescheduledEvent, PendingRescheduledEvent, RejectedRescheduledEvent
from src.types.user import User, UserId


class InitialState(BaseModel):
    user: User


class StateWithCalendar(InitialState):
    calendar: Calendar


class StateWithInvitees(StateWithCalendar):
    invitees: Sequence[User]
    invitee_calendars: dict[UserId, Calendar] = Field(default_factory=dict)


class StateWithPendingReschedulingProposals(StateWithInvitees):
    pending_rescheduling_proposals: list[PendingRescheduledEvent]


class StateWithCompletedReschedulingProposals(StateWithPendingReschedulingProposals):
    completed_rescheduling_proposals: list[AcceptedRescheduledEvent | RejectedRescheduledEvent]


def load_calendar(state: InitialState) -> StateWithCalendar:
    return StateWithCalendar(user=state.user, calendar=my_calendar)


def load_invitees(state: StateWithCalendar) -> StateWithInvitees:
    return StateWithInvitees(
        user=state.user,
        calendar=state.calendar,
        invitees=[adams_user, sallys_user],
        invitee_calendars={adams_user_id: adams_calendar, sallys_user_id: sallys_calendar},
    )


async def get_rescheduling_proposals(state: StateWithInvitees) -> StateWithPendingReschedulingProposals:
    date = datetime(2025, 8, 11, tzinfo=ZoneInfo(me.timezone))
    # other_invitees = [(adams_user, adams_calendar), (sallys_user, sallys_calendar)]
    # pending_rescheduling_proposals = await generate_rescheduling_proposals(date, me, my_calendar, other_invitees)
    pending_rescheduling_proposals = [
        PendingRescheduledEvent(
            event_id=str(my_calendar.get_events_on(date)[0].id),
            new_start_time=datetime(2025, 8, 11, 12, 0, 0, tzinfo=ZoneInfo(me.timezone)),
            new_end_time=datetime(2025, 8, 11, 13, 0, 0, tzinfo=ZoneInfo(me.timezone)),
            explanation="I need to reschedule this event because I have a conflict.",
        ),
    ]

    return StateWithPendingReschedulingProposals(
        user=state.user,
        calendar=state.calendar,
        invitees=state.invitees,
        invitee_calendars=state.invitee_calendars,
        pending_rescheduling_proposals=pending_rescheduling_proposals,
    )


async def submit_rescheduling_proposals(state: StateWithPendingReschedulingProposals) -> StateWithCompletedReschedulingProposals:
    pending_rescheduling_proposals = state.pending_rescheduling_proposals
    print("Rescheduling proposals:")
    completed_rescheduling_proposals: list[AcceptedRescheduledEvent | RejectedRescheduledEvent] = []
    for pending_rescheduling_proposal in pending_rescheduling_proposals:
        print("Event ID:", str(pending_rescheduling_proposal.event_id)[:8])
        print("New start time:", pending_rescheduling_proposal.new_start_time.hour)
        print("New end time:", pending_rescheduling_proposal.new_end_time.hour)
        print("Explanation:", pending_rescheduling_proposal.explanation)

        result = await submit_rescheduling_proposal(state.user, pending_rescheduling_proposal)
        completed_rescheduling_proposals.append(result)
        print("Accepted:", isinstance(result, AcceptedRescheduledEvent))
        print()

    return StateWithCompletedReschedulingProposals(
        user=state.user,
        calendar=state.calendar,
        invitees=state.invitees,
        invitee_calendars=state.invitee_calendars,
        pending_rescheduling_proposals=pending_rescheduling_proposals,
        completed_rescheduling_proposals=completed_rescheduling_proposals,
    )


def summarization(state: StateWithCompletedReschedulingProposals) -> StateWithCompletedReschedulingProposals:
    summary = summarize_rescheduling_proposals(state.completed_rescheduling_proposals)
    print(summary)
    return state


graph = StateGraph(InitialState)

# Set the entry point state type
graph.set_entry_point("load_calendar")

graph.add_node("load_calendar", load_calendar)
graph.add_node("load_invitees", load_invitees)
graph.add_node("get_rescheduling_proposals", get_rescheduling_proposals)
graph.add_node("submit_rescheduling_proposals", submit_rescheduling_proposals)
graph.add_node("summarization", summarization)

graph.add_edge("load_calendar", "load_invitees")
graph.add_edge("load_invitees", "get_rescheduling_proposals")
graph.add_edge("get_rescheduling_proposals", "submit_rescheduling_proposals")
graph.add_edge("submit_rescheduling_proposals", "summarization")
graph.add_edge("summarization", END)


compiled_graph = graph.compile()


async def main() -> None:
    initial_state = InitialState(user=me)
    await compiled_graph.ainvoke(initial_state)


if __name__ == "__main__":
    asyncio.run(main())
