import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from src.config.main import config
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.send_message.types import SendMessageResponse
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.types import InitialState
from src.types.messaging import OutgoingMessage


async def send_message(state: InitialState) -> SendMessageResponse:
    await asyncio.sleep(config.delay_seconds_send_rescheduling_proposal_to_invitee_send_message)
    return SendMessageResponse(
        sent_message=OutgoingMessage(
            platform_id="slack",
            content="I need to reschedule this event because I have a conflict.",
            sent_at=datetime.now(ZoneInfo(state.user.timezone)),
            from_user=state.user,
            to_user=state.invitee,
        ),
    )
