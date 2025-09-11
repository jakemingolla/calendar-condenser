from src.agents.messaging import determine_rescheduling_proposal_resolution
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.analyze_message.types import AnalyzeMessageResponse
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.types import StateWithReceivedMessage
from src.types.rescheduled_event import AcceptedRescheduledEvent


async def analyze_message(state: StateWithReceivedMessage) -> AnalyzeMessageResponse:
    resolution = await determine_rescheduling_proposal_resolution(
        state.pending_rescheduling_proposals[0],
        state.sent_message.content,
        state.received_message.content,
    )
    return AnalyzeMessageResponse(
        message_analysis="positive" if isinstance(resolution, AcceptedRescheduledEvent) else "negative",
    )
