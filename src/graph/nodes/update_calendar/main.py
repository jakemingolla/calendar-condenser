import asyncio
from typing import TYPE_CHECKING

from src.config.main import config
from src.domains.calendar.mock_calendar import my_calendar

if TYPE_CHECKING:
    from src.types.calendar_event import CalendarEventId

from src.types.state import StateAfterSendingReschedulingProposals
from src.utilities.loading import indicate_loading


async def update_calendar(state: StateAfterSendingReschedulingProposals) -> None:
    updated_events: dict[CalendarEventId, bool] = {}
    indicate_loading("Updating your calendar...")

    for accepted_rescheduling_proposal in state.accepted_rescheduling_proposals:
        updated_events[accepted_rescheduling_proposal.original_event.id] = True

        await my_calendar.change_event_time(
            accepted_rescheduling_proposal.original_event.id,
            accepted_rescheduling_proposal.new_start_time,
            accepted_rescheduling_proposal.new_end_time,
        )

    await asyncio.sleep(config.delay_seconds_update_calendar)
