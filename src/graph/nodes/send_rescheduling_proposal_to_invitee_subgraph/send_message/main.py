import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from src.config.main import config
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.send_message.types import SendMessageResponse
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.types import InitialState
from src.types.messaging import OutgoingMessage
from src.utilities.timestamp_formatting import format_time_human_friendly


async def send_message(state: InitialState) -> SendMessageResponse:
    await asyncio.sleep(config.delay_seconds_send_rescheduling_proposal_to_invitee_send_message)
    rescheduling_proposal = state.pending_rescheduling_proposals[0]

    event_title = rescheduling_proposal.original_event.title
    start_time = format_time_human_friendly(rescheduling_proposal.new_start_time)
    end_time = format_time_human_friendly(rescheduling_proposal.new_end_time)
    end_time_am_pm = rescheduling_proposal.new_end_time.strftime("%p")

    content = f"Hey, is it alright if we reschedule {event_title} to {start_time} - {end_time}{end_time_am_pm}?"

    return SendMessageResponse(
        sent_message=OutgoingMessage(
            platform_id="slack",
            content=content,
            sent_at=datetime.now(ZoneInfo(state.user.timezone)),
            from_user=state.user,
            to_user=state.invitee,
        ),
    )
