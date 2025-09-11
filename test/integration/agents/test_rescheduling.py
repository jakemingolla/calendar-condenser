import pytest

from src.agents.rescheduling import generate_rescheduling_proposals
from src.domains.calendar.mock_calendar import adams_calendar, my_calendar, sallys_calendar
from src.domains.user.mock_user_provider import adams_user, me, sallys_user


@pytest.mark.asyncio
async def test_generate_rescheduling_proposals():
    other_invitees = [(adams_user, adams_calendar), (sallys_user, sallys_calendar)]
    date = my_calendar.events[0].start_time
    pending_rescheduling_proposals = await generate_rescheduling_proposals(date, me, my_calendar, other_invitees)

    assert len(pending_rescheduling_proposals) == 1

    proposal = pending_rescheduling_proposals[0]
    matching_event = next(filter(lambda event: event.title == "Team Brainstorming", my_calendar.events))

    assert proposal.original_event.id == matching_event.id
    assert proposal.new_start_time.hour == 12
    assert proposal.new_end_time.hour == 13
