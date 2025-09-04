from datetime import datetime
from zoneinfo import ZoneInfo

from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.receive_message.types import ReceiveMessageResponse
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.types import StateWithSentMessage
from src.types.messaging import IncomingMessage


async def receive_message(state: StateWithSentMessage) -> ReceiveMessageResponse:
    return ReceiveMessageResponse(
        received_message=IncomingMessage(
            platform_id="slack",
            content="Yes, that works for me.",
            sent_at=datetime.now(ZoneInfo(state.user.timezone)),
            from_user=state.invitee,
            to_user=state.user,
        ),
    )
