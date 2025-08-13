import asyncio
from collections.abc import Sequence
from datetime import datetime
from zoneinfo import ZoneInfo

from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from src.agents.messaging import submit_rescheduling_proposal
from src.agents.rescheduling import generate_rescheduling_proposals
from src.agents.summary import summarize_rescheduling_proposals
from src.domains.mock_user.mock_user_provider import MockUserProvider, adams_user, adams_user_id, me, sallys_user, sallys_user_id
from src.graph.mock_data import (
    adams_calendar,
    my_calendar,
    sallys_calendar,
)
from src.types.calendar import Calendar
from src.types.rescheduled_event import AcceptedRescheduledEvent, PendingRescheduledEvent, RejectedRescheduledEvent
from src.types.user import User, UserId

user_provider = MockUserProvider()


class State(BaseModel):
    date: datetime


class InitialState(State):
    user: User


class StateWithCalendar(InitialState):
    calendar: Calendar


class StateWithInvitees(StateWithCalendar):
    invitees: Sequence[User]
    invitee_calendars: dict[UserId, Calendar] = Field(default_factory=dict)


class StateWithPendingReschedulingProposals(StateWithInvitees):
    # TODO This needs to be able to handle multiple proposals for different events.
    pending_rescheduling_proposals: list[PendingRescheduledEvent]


class StateWithCompletedReschedulingProposals(StateWithPendingReschedulingProposals):
    completed_rescheduling_proposals: list[AcceptedRescheduledEvent | RejectedRescheduledEvent]


def load_calendar(state: InitialState) -> StateWithCalendar:
    return StateWithCalendar(user=state.user, calendar=my_calendar, date=state.date)


def load_invitees(state: StateWithCalendar) -> StateWithInvitees:
    return StateWithInvitees(
        user=state.user,
        calendar=state.calendar,
        date=state.date,
        invitees=[adams_user, sallys_user],
        invitee_calendars={adams_user_id: adams_calendar, sallys_user_id: sallys_calendar},
    )


def print_all_events(state: StateWithInvitees) -> StateWithInvitees:
    seen_events = set()
    formatted_date = state.date.strftime("%Y-%m-%d")
    print(f"{state.user.given_name} events:")
    for event in state.calendar.get_events_on(state.date):
        seen_events.add(event.id)
        print(f"- {event.title} ({event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')})")
    print()

    for invitee, calendar in zip(state.invitees, state.invitee_calendars.values(), strict=True):
        additional_events = calendar.get_events_on(state.date)
        unique_events = [event for event in additional_events if event.id not in seen_events]
        if len(unique_events) > 0:
            print(f"{invitee.given_name} events:")
            for event in unique_events:
                print(f"- {event.title} ({event.start_time} - {event.end_time})")
            print()
            seen_events.update(event.id for event in unique_events)
        else:
            print(f"{invitee.given_name} has no additional events on {formatted_date}.")
    print()
    return state


async def get_rescheduling_proposals(state: StateWithInvitees) -> StateWithPendingReschedulingProposals:
    other_invitees = [(adams_user, adams_calendar), (sallys_user, sallys_calendar)]
    pending_rescheduling_proposals = await generate_rescheduling_proposals(state.date, me, my_calendar, other_invitees)
    # pending_rescheduling_proposals = [
    #     PendingRescheduledEvent(
    #         original_event=my_calendar.get_events_on(state.date)[0],
    #         new_start_time=datetime(2025, 8, 11, 12, 0, 0, tzinfo=ZoneInfo(me.timezone)),
    #         new_end_time=datetime(2025, 8, 11, 13, 0, 0, tzinfo=ZoneInfo(me.timezone)),
    #         explanation="I need to reschedule this event because I have a conflict.",
    #     ),
    # ]

    return StateWithPendingReschedulingProposals(
        user=state.user,
        date=state.date,
        calendar=state.calendar,
        invitees=state.invitees,
        invitee_calendars=state.invitee_calendars,
        pending_rescheduling_proposals=pending_rescheduling_proposals,
    )


async def submit_rescheduling_proposals(state: StateWithPendingReschedulingProposals) -> StateWithCompletedReschedulingProposals:
    pending_rescheduling_proposals = state.pending_rescheduling_proposals
    completed_rescheduling_proposals: list[AcceptedRescheduledEvent | RejectedRescheduledEvent] = []
    print("Rescheduling proposals:")
    for pending_rescheduling_proposal in pending_rescheduling_proposals:
        print("Event ID:", str(pending_rescheduling_proposal.original_event.id)[:8])
        print("New start time:", pending_rescheduling_proposal.new_start_time.hour)
        print("New end time:", pending_rescheduling_proposal.new_end_time.hour)
        print()

        results: list[AcceptedRescheduledEvent | RejectedRescheduledEvent] = []
        print(f"Submitting rescheduling proposal to {len(pending_rescheduling_proposal.original_event.invitees)} invitees...")
        print("Explanation:", pending_rescheduling_proposal.explanation)
        print()

        for invitee in pending_rescheduling_proposal.original_event.invitees:
            user = user_provider.get_user(invitee.id)
            result = await submit_rescheduling_proposal(user, pending_rescheduling_proposal)
            results.append(result)
            completed_rescheduling_proposals.append(result)
            print(f"{user.given_name} accepted: ", isinstance(result, AcceptedRescheduledEvent))

    return StateWithCompletedReschedulingProposals(
        user=state.user,
        date=state.date,
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
graph.add_node("print_all_events", print_all_events)
graph.add_node("get_rescheduling_proposals", get_rescheduling_proposals)
graph.add_node("submit_rescheduling_proposals", submit_rescheduling_proposals)
graph.add_node("summarization", summarization)

graph.add_edge("load_calendar", "load_invitees")
graph.add_edge("load_invitees", "print_all_events")
graph.add_edge("print_all_events", "get_rescheduling_proposals")
graph.add_edge("get_rescheduling_proposals", "submit_rescheduling_proposals")
graph.add_edge("submit_rescheduling_proposals", "summarization")
graph.add_edge("summarization", END)


compiled_graph = graph.compile()


async def main() -> None:
    date = datetime(2025, 8, 11, tzinfo=ZoneInfo(me.timezone))
    print("User:", me.given_name)
    print("Date:", date)
    print()
    initial_state = InitialState(user=me, date=date)
    await compiled_graph.ainvoke(initial_state)


if __name__ == "__main__":
    asyncio.run(main())
