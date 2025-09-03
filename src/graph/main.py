from datetime import datetime
from typing import Literal, TypedDict
from zoneinfo import ZoneInfo

from langgraph.graph import END, StateGraph
from langgraph.types import Send, interrupt

from src.agents.guide import anticipate_rescheduling_proposals, introduction_to_user, summarize_state_with_calendar
from src.agents.summary import summarize_rescheduling_proposals
from src.domains.mock_calendar.mock_calendar import adams_calendar, my_calendar, sallys_calendar
from src.domains.mock_user.mock_user_provider import MockUserProvider, adams_user, adams_user_id, me, sallys_user, sallys_user_id
from src.graph.send_rescheduling_proposal_to_invitee import (
    InitialState as SendReschedulingProposalToInviteeInitialState,
)
from src.graph.send_rescheduling_proposal_to_invitee import (
    uncompiled_graph as send_rescheduling_proposal_to_invitee_uncompiled_graph,
)
from src.types.messaging import IncomingMessage, OutgoingMessage
from src.types.rescheduled_event import PendingRescheduledEvent
from src.types.state import (
    InitialState,
    StateWithCalendar,
    StateWithCompletedReschedulingProposals,
    StateWithInviteeMessages,
    StateWithInvitees,
    StateWithPendingReschedulingProposals,
)
from src.types.user import UserId

user_provider = MockUserProvider()
send_rescheduling_proposal_to_invitee_subgraph = send_rescheduling_proposal_to_invitee_uncompiled_graph.compile()


async def introduction(state: InitialState) -> InitialState:
    if False:
        await introduction_to_user(state.user, state.date)
    return state


async def confirm_start(state: InitialState) -> InitialState:
    value = interrupt(
        "Do you want to start the rescheduling process?",
    )
    assert value == "CONFIRMED"  # TODO Handle other values
    return state


async def load_calendar(state: InitialState) -> StateWithCalendar:
    # await asyncio.sleep(2)
    return StateWithCalendar.from_previous_state(state, calendar=my_calendar)


async def summarize_calendar(state: StateWithCalendar) -> StateWithCalendar:
    if False:
        await summarize_state_with_calendar(state)
    return state


async def load_invitees(state: StateWithCalendar) -> StateWithInvitees:
    # await asyncio.sleep(2)
    return StateWithInvitees.from_previous_state(
        state,
        invitees=[adams_user, sallys_user],
        invitee_calendars={adams_user_id: adams_calendar, sallys_user_id: sallys_calendar},
    )


async def before_rescheduling_proposals(state: StateWithInvitees) -> StateWithInvitees:
    if False:
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
    # await asyncio.sleep(3)

    return StateWithPendingReschedulingProposals.from_previous_state(
        state,
        pending_rescheduling_proposals=pending_rescheduling_proposals,
    )


async def confirm_rescheduling_proposals(state: StateWithPendingReschedulingProposals) -> StateWithPendingReschedulingProposals:
    value = interrupt(
        "Do these rescheduling proposals look good?",
    )
    assert value == "CONFIRMED"  # TODO Handle other values
    return state


class InvokeSendReschedulingProposalToInviteeOutput(TypedDict):
    invitee_messages: dict[UserId, list[IncomingMessage | OutgoingMessage]]


async def invoke_send_rescheduling_proposal_to_invitee(
    subgraph_input: SendReschedulingProposalToInviteeInitialState,
) -> dict[Literal["conversations_by_invitee"], dict[UserId, list[IncomingMessage | OutgoingMessage]]]:
    subgraph_output = await send_rescheduling_proposal_to_invitee_subgraph.ainvoke(input=subgraph_input)
    sent_message: OutgoingMessage = subgraph_output["sent_message"]
    received_message: IncomingMessage = subgraph_output["received_message"]
    return {
        "conversations_by_invitee": {
            subgraph_input.invitee.id: [sent_message, received_message],
        },
    }


async def send_rescheduling_proposal_to_invitees(state: StateWithPendingReschedulingProposals) -> list[Send]:
    return [
        Send(
            "invoke_send_rescheduling_proposal_to_invitee",
            SendReschedulingProposalToInviteeInitialState(
                user=state.user,
                invitee=invitee,  # TODO: Handle multiple invitees
                pending_rescheduling_proposals=state.pending_rescheduling_proposals,
            ),
        )
        for invitee in state.invitees
    ]


async def extract_completed_rescheduling_proposals(
    state: StateWithInviteeMessages,
) -> StateWithCompletedReschedulingProposals:
    return StateWithCompletedReschedulingProposals.from_previous_state(state, completed_rescheduling_proposals=[])


async def summarization(state: StateWithCompletedReschedulingProposals) -> StateWithCompletedReschedulingProposals:
    if False:
        summary = summarize_rescheduling_proposals(state.completed_rescheduling_proposals)
        print(summary)
    return state


uncompiled_graph = StateGraph(InitialState)

uncompiled_graph.set_entry_point("introduction")

uncompiled_graph.add_node("introduction", introduction)
uncompiled_graph.add_node("confirm_start", confirm_start)
uncompiled_graph.add_node("summarize_calendar", summarize_calendar)
uncompiled_graph.add_node("load_calendar", load_calendar)
uncompiled_graph.add_node("load_invitees", load_invitees)
uncompiled_graph.add_node("before_rescheduling_proposals", before_rescheduling_proposals)
uncompiled_graph.add_node("get_rescheduling_proposals", get_rescheduling_proposals)
uncompiled_graph.add_node("confirm_rescheduling_proposals", confirm_rescheduling_proposals)
uncompiled_graph.add_node("send_rescheduling_proposal_to_invitees", send_rescheduling_proposal_to_invitees)
uncompiled_graph.add_node("invoke_send_rescheduling_proposal_to_invitee", invoke_send_rescheduling_proposal_to_invitee)
uncompiled_graph.add_node("extract_completed_rescheduling_proposals", extract_completed_rescheduling_proposals)
uncompiled_graph.add_node("summarization", summarization)

uncompiled_graph.add_edge("introduction", "confirm_start")
uncompiled_graph.add_edge("confirm_start", "load_calendar")
uncompiled_graph.add_edge("load_calendar", "summarize_calendar")
uncompiled_graph.add_edge("summarize_calendar", "load_invitees")
uncompiled_graph.add_edge("load_invitees", "before_rescheduling_proposals")
uncompiled_graph.add_edge("before_rescheduling_proposals", "get_rescheduling_proposals")
uncompiled_graph.add_edge("get_rescheduling_proposals", "confirm_rescheduling_proposals")
uncompiled_graph.add_conditional_edges(
    "confirm_rescheduling_proposals",
    send_rescheduling_proposal_to_invitees,
    ["invoke_send_rescheduling_proposal_to_invitee"],
)
uncompiled_graph.add_edge("invoke_send_rescheduling_proposal_to_invitee", "extract_completed_rescheduling_proposals")
uncompiled_graph.add_edge("extract_completed_rescheduling_proposals", "summarization")
uncompiled_graph.add_edge("summarization", END)


compiled_graph = uncompiled_graph.compile()
