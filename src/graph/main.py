import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from langgraph.graph import END, StateGraph
from langgraph.types import interrupt

from src.agents.guide import anticipate_rescheduling_proposals, introduction_to_user, summarize_state_with_calendar
from src.agents.messaging import submit_rescheduling_proposal
from src.agents.summary import summarize_rescheduling_proposals
from src.domains.mock_calendar.mock_calendar import adams_calendar, my_calendar, sallys_calendar
from src.domains.mock_user.mock_user_provider import MockUserProvider, adams_user, adams_user_id, me, sallys_user, sallys_user_id
from src.types.rescheduled_event import AcceptedRescheduledEvent, PendingRescheduledEvent, RejectedRescheduledEvent
from src.types.state import (
    InitialState,
    StateWithCalendar,
    StateWithCompletedReschedulingProposals,
    StateWithInvitees,
    StateWithPendingReschedulingProposals,
)

user_provider = MockUserProvider()


async def introduction(state: InitialState) -> InitialState:
    await introduction_to_user(state.user, state.date)
    value = interrupt(
        "Do you want to start the rescheduling process?",
    )
    assert value == "Yes"  # TODO Handle other values
    return state


async def load_calendar(state: InitialState) -> StateWithCalendar:
    await asyncio.sleep(2)
    return StateWithCalendar.from_previous_state(state, calendar=my_calendar)


async def summarize_calendar(state: StateWithCalendar) -> StateWithCalendar:
    await summarize_state_with_calendar(state)
    return state


async def load_invitees(state: StateWithCalendar) -> StateWithInvitees:
    await asyncio.sleep(2)
    return StateWithInvitees.from_previous_state(
        state,
        invitees=[adams_user, sallys_user],
        invitee_calendars={adams_user_id: adams_calendar, sallys_user_id: sallys_calendar},
    )


async def before_rescheduling_proposals(state: StateWithInvitees) -> StateWithInvitees:
    await anticipate_rescheduling_proposals(state)
    return state


async def get_rescheduling_proposals(state: StateWithInvitees) -> StateWithPendingReschedulingProposals:
    # other_invitees = [(adams_user, adams_calendar), (sallys_user, sallys_calendar)]
    # pending_rescheduling_proposals = await generate_rescheduling_proposals(state.date, me, my_calendar, other_invitees)
    pending_rescheduling_proposals = [
        PendingRescheduledEvent(
            original_event=my_calendar.get_events_on(state.date)[0],
            new_start_time=datetime(2025, 8, 11, 12, 0, 0, tzinfo=ZoneInfo(me.timezone)),
            new_end_time=datetime(2025, 8, 11, 13, 0, 0, tzinfo=ZoneInfo(me.timezone)),
            explanation="I need to reschedule this event because I have a conflict.",
        ),
    ]
    await asyncio.sleep(3)

    return StateWithPendingReschedulingProposals.from_previous_state(
        state,
        pending_rescheduling_proposals=pending_rescheduling_proposals,
    )


async def confirm_rescheduling_proposals(state: StateWithPendingReschedulingProposals) -> StateWithPendingReschedulingProposals:
    value = interrupt(
        "Do these rescheduling proposals look good?",
    )
    assert value == "Yes"  # TODO Handle other values
    return state


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

    return StateWithCompletedReschedulingProposals.from_previous_state(
        state,
        completed_rescheduling_proposals=completed_rescheduling_proposals,
    )


def summarization(state: StateWithCompletedReschedulingProposals) -> StateWithCompletedReschedulingProposals:
    summary = summarize_rescheduling_proposals(state.completed_rescheduling_proposals)
    print(summary)
    print(state.model_dump_json())
    return state


uncompiled_graph = StateGraph(InitialState)

uncompiled_graph.set_entry_point("introduction")

uncompiled_graph.add_node("introduction", introduction)
uncompiled_graph.add_node("summarize_calendar", summarize_calendar)
uncompiled_graph.add_node("load_calendar", load_calendar)
uncompiled_graph.add_node("load_invitees", load_invitees)
uncompiled_graph.add_node("before_rescheduling_proposals", before_rescheduling_proposals)
uncompiled_graph.add_node("get_rescheduling_proposals", get_rescheduling_proposals)
uncompiled_graph.add_node("confirm_rescheduling_proposals", confirm_rescheduling_proposals)
uncompiled_graph.add_node("submit_rescheduling_proposals", submit_rescheduling_proposals)
uncompiled_graph.add_node("summarization", summarization)

uncompiled_graph.add_edge("introduction", "load_calendar")
uncompiled_graph.add_edge("load_calendar", "summarize_calendar")
uncompiled_graph.add_edge("summarize_calendar", "load_invitees")
uncompiled_graph.add_edge("load_invitees", "before_rescheduling_proposals")
uncompiled_graph.add_edge("before_rescheduling_proposals", "get_rescheduling_proposals")
uncompiled_graph.add_edge("get_rescheduling_proposals", "confirm_rescheduling_proposals")
uncompiled_graph.add_edge("confirm_rescheduling_proposals", END)

# uncompiled_graph.add_edge("get_rescheduling_proposals", "submit_rescheduling_proposals")
# uncompiled_graph.add_edge("submit_rescheduling_proposals", "summarization")
# uncompiled_graph.add_edge("summarization", END)


compiled_graph = uncompiled_graph.compile()
