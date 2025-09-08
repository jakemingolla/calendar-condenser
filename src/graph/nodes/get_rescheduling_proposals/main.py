import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from src.domains.mock_calendar.mock_calendar import my_calendar
from src.graph.nodes.get_rescheduling_proposals.types import GetReschedulingProposalsResponse
from src.types.rescheduled_event import PendingRescheduledEvent
from src.types.state import StateWithInvitees
from src.utilities.loading import indicate_loading


async def get_rescheduling_proposals(state: StateWithInvitees) -> GetReschedulingProposalsResponse:
    # other_invitees = [(adams_user, adams_calendar), (sallys_user, sallys_calendar)]
    # pending_rescheduling_proposals = await generate_rescheduling_proposals(state.date, me, my_calendar, other_invitees)
    pending_rescheduling_proposals = [
        PendingRescheduledEvent(
            original_event=my_calendar.get_events_on(state.date)[0],
            new_start_time=datetime(2025, 8, 11, 12, 0, 0, tzinfo=ZoneInfo(state.user.timezone)),
            new_end_time=datetime(2025, 8, 11, 13, 0, 0, tzinfo=ZoneInfo(state.user.timezone)),
            explanation="I need to reschedule this event because I have a conflict.",
        ),
    ]

    indicate_loading("Generating rescheduling proposals...")
    await asyncio.sleep(3)

    return GetReschedulingProposalsResponse(
        pending_rescheduling_proposals=pending_rescheduling_proposals,
    )
