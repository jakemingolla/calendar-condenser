import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from src.config.main import config
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.receive_message.types import ReceiveMessageResponse
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.types import StateWithSentMessage
from src.types.messaging import IncomingMessage
from src.utilities.sentiment import get_positive_response


async def receive_message(state: StateWithSentMessage) -> ReceiveMessageResponse:
    await asyncio.sleep(config.delay_seconds_send_rescheduling_proposal_to_invitee_receive_message)
    return ReceiveMessageResponse(
        received_message=IncomingMessage(
            platform_id="slack",
            content=get_positive_response(),
            sent_at=datetime.now(ZoneInfo(state.user.timezone)),
            from_user=state.invitee,
            to_user=state.user,
        ),
    )
