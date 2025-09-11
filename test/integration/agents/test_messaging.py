from datetime import timedelta

import pytest

from src.agents.messaging import determine_rescheduling_proposal_resolution
from src.types.calendar_event import CalendarEvent
from src.types.rescheduled_event import AcceptedRescheduledEvent, PendingRescheduledEvent, RejectedRescheduledEvent
from src.utilities.sentiment import get_negative_response, get_positive_response


@pytest.fixture
def pending_rescheduling_proposal(mock_event: CalendarEvent) -> PendingRescheduledEvent:
    return PendingRescheduledEvent(
        original_event=mock_event,
        explanation="Test Explanation",
        new_start_time=mock_event.start_time + timedelta(hours=1),
        new_end_time=mock_event.end_time + timedelta(hours=1),
    )


@pytest.mark.asyncio
async def test_determine_rescheduling_proposal_resolution_positive(pending_rescheduling_proposal: PendingRescheduledEvent):
    resolution = await determine_rescheduling_proposal_resolution(
        pending_rescheduling_proposal,
        "Hi, can we move Team Brainstorming to 12 - 1pm?",
        get_positive_response(),
    )
    assert isinstance(resolution, AcceptedRescheduledEvent)


@pytest.mark.asyncio
async def test_determine_rescheduling_proposal_resolution_negative(pending_rescheduling_proposal: PendingRescheduledEvent):
    resolution = await determine_rescheduling_proposal_resolution(
        pending_rescheduling_proposal,
        "Hi, can we move Team Brainstorming to 12 - 1pm?",
        get_negative_response(),
    )
    assert isinstance(resolution, RejectedRescheduledEvent)
