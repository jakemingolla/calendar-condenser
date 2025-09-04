import asyncio

from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.analyze_message.types import AnalyzeMessageResponse
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.types import StateWithReceivedMessage


async def analyze_message(state: StateWithReceivedMessage) -> AnalyzeMessageResponse:
    await asyncio.sleep(3)
    return AnalyzeMessageResponse(
        message_analysis="positive",
    )
