from typing import TYPE_CHECKING

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.analyze_message.main import analyze_message
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.receive_message.main import receive_message
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.send_message.main import send_message
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.types import (
    InitialState,
    InvokeSendReschedulingProposalResponse,
    StateWithMessageAnalysis,
)
from src.types.state import StateWithPendingReschedulingProposals

if TYPE_CHECKING:
    from src.types.messaging import IncomingMessage, OutgoingMessage

uncompiled_graph = StateGraph(
    state_schema=StateWithMessageAnalysis,
    input_schema=InitialState,
    output_schema=StateWithMessageAnalysis,
)
uncompiled_graph.add_node("send_message", send_message)
uncompiled_graph.add_node("receive_message", receive_message)
uncompiled_graph.add_node("analyze_message", analyze_message)

uncompiled_graph.add_edge(START, "send_message")
uncompiled_graph.add_edge("send_message", "receive_message")
uncompiled_graph.add_edge("receive_message", "analyze_message")
uncompiled_graph.add_edge("analyze_message", END)

compiled_graph = uncompiled_graph.compile()


async def invoke_send_rescheduling_proposal_to_invitee(
    subgraph_input: InitialState,
) -> InvokeSendReschedulingProposalResponse:
    subgraph_output = await compiled_graph.ainvoke(input=subgraph_input)
    sent_message: OutgoingMessage = subgraph_output["sent_message"]
    received_message: IncomingMessage = subgraph_output["received_message"]
    return InvokeSendReschedulingProposalResponse(
        conversations_by_invitee={
            subgraph_input.invitee.id: [sent_message, received_message],
        },
    )


async def send_rescheduling_proposal_to_invitees(state: StateWithPendingReschedulingProposals) -> list[Send]:
    return [
        Send(
            "invoke_send_rescheduling_proposal_to_invitee",
            InitialState(
                user=state.user,
                invitee=invitee,  # TODO: Handle multiple invitees
                pending_rescheduling_proposals=state.pending_rescheduling_proposals,
            ),
        )
        for invitee in state.invitees
    ]
