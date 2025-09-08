import asyncio

from src.config.main import config
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.analyze_message.types import AnalyzeMessageResponse
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.types import StateWithReceivedMessage


async def analyze_message(state: StateWithReceivedMessage) -> AnalyzeMessageResponse:
    await asyncio.sleep(config.delay_seconds_send_rescheduling_proposal_to_invitee_analyze_message)
    return AnalyzeMessageResponse(
        message_analysis="positive",
    )
