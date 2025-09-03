from typing import Literal, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.types import Send

from src.domains.mock_user.mock_user_provider import MockUserProvider
from src.graph.nodes.before_rescheduling_proposals.main import before_rescheduling_proposals
from src.graph.nodes.confirm_rescheduling_proposals.main import confirm_rescheduling_proposals
from src.graph.nodes.confirm_start.main import confirm_start
from src.graph.nodes.final_summarization.main import final_summarization
from src.graph.nodes.get_rescheduling_proposals.main import get_rescheduling_proposals
from src.graph.nodes.introduction.main import introduction
from src.graph.nodes.load_calendar.main import load_calendar
from src.graph.nodes.load_invitees.main import load_invitees
from src.graph.nodes.summarize_calendar.main import summarize_calendar
from src.graph.send_rescheduling_proposal_to_invitee import (
    InitialState as SendReschedulingProposalToInviteeInitialState,
)
from src.graph.send_rescheduling_proposal_to_invitee import (
    uncompiled_graph as send_rescheduling_proposal_to_invitee_uncompiled_graph,
)
from src.types.messaging import IncomingMessage, OutgoingMessage
from src.types.state import (
    InitialState,
    StateWithPendingReschedulingProposals,
)
from src.types.user import UserId

user_provider = MockUserProvider()
send_rescheduling_proposal_to_invitee_subgraph = send_rescheduling_proposal_to_invitee_uncompiled_graph.compile()


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
uncompiled_graph.add_node("invoke_send_rescheduling_proposal_to_invitee", invoke_send_rescheduling_proposal_to_invitee)  # type: ignore TODO
uncompiled_graph.add_node("final_summarization", final_summarization)

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
uncompiled_graph.add_edge("invoke_send_rescheduling_proposal_to_invitee", "final_summarization")
uncompiled_graph.add_edge("final_summarization", END)


compiled_graph = uncompiled_graph.compile()
