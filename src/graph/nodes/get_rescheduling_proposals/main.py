import asyncio

from src.agents.rescheduling import generate_rescheduling_proposals
from src.config.main import config
from src.domains.calendar.mock_calendar import adams_calendar, my_calendar, sallys_calendar
from src.domains.user.mock_user_provider import adams_user, me, sallys_user
from src.graph.nodes.get_rescheduling_proposals.types import GetReschedulingProposalsResponse
from src.types.state import StateWithInvitees
from src.utilities.loading import indicate_loading


async def get_rescheduling_proposals(state: StateWithInvitees) -> GetReschedulingProposalsResponse:
    indicate_loading("Generating rescheduling proposals...")
    await asyncio.sleep(config.delay_seconds_get_rescheduling_proposals)

    other_invitees = [(adams_user, adams_calendar), (sallys_user, sallys_calendar)]
    pending_rescheduling_proposals = await generate_rescheduling_proposals(state.date, me, my_calendar, other_invitees)
    # pending_rescheduling_proposals = [
    #     PendingRescheduledEvent(
    #         original_event=my_calendar.get_events_on(state.date)[0],
    #         new_start_time=datetime(2025, 8, 11, 12, 0, 0, tzinfo=ZoneInfo(state.user.timezone)),
    #         new_end_time=datetime(2025, 8, 11, 13, 0, 0, tzinfo=ZoneInfo(state.user.timezone)),
    #         explanation="I need to reschedule this event because I have a conflict.",
    #     ),
    # ]

    return GetReschedulingProposalsResponse(
        pending_rescheduling_proposals=pending_rescheduling_proposals,
    )
