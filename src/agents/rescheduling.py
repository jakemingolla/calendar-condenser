from collections.abc import Sequence
from datetime import datetime
from typing import cast

from pydantic import BaseModel, Field

from src.agents.helpers.models import get_llm
from src.agents.helpers.serialization import serialize_event
from src.config.main import config
from src.types.calendar import Calendar
from src.types.calendar_event import CalendarEventId
from src.types.rescheduled_event import AcceptedRescheduledEvent, PendingRescheduledEvent
from src.types.user import User


class EventReschedulingProposal(BaseModel):
    event_id: CalendarEventId
    new_start_time: datetime
    new_end_time: datetime
    explanation: str


class ReschedulingProposal(BaseModel):
    events: list[EventReschedulingProposal] = Field(
        description="A list of rescheduling proposals for events.",
    )


unstructured_llm = get_llm(source="rescheduling.private", model=config.rescheduling_agent_model)
structured_llm = get_llm(source="rescheduling.structured_output").with_structured_output(
    ReschedulingProposal,
    method="json_schema",
)


def serialize_invitee_other_events_on(date: datetime, invitee: User, calendar: Calendar, subject: User) -> str:
    invitees_events = calendar.get_events_on(date)
    invitees_events_not_owned_by_subject = list(
        filter(lambda event: event.owner != subject.id, invitees_events),
    )
    if len(invitees_events_not_owned_by_subject) == 0:
        return f"{invitee.given_name} has no other events scheduled on {date.strftime('%Y-%m-%d')}.\n"
    else:
        return f"{invitee.given_name} has these additional events scheduled on {date.strftime('%Y-%m-%d')}:\n" + "".join(
            serialize_event(event, include_id=False) for event in invitees_events_not_owned_by_subject
        )


async def generate_rescheduling_proposals(
    date: datetime,
    user: User,
    users_calendar: Calendar,
    other_invitees: Sequence[tuple[User, Calendar]],
) -> list[PendingRescheduledEvent]:
    """Generate a rescheduling proposal for a calendar event."""
    users_events = users_calendar.get_events_on(date)
    baseline_context = "".join(
        (
            "- You are an assistant that can help with calendar events.\n",
            f"- The current date is {date.strftime('%Y-%m-%d')}.\n"
            f"- You are speaking with {user.given_name}. Their user ID is {user.id!s}.\n"
            f"- The user's timezone is {user.timezone}.\n",
            "- All times mentioned are in the user's local timezone on the current date.\n",
            "- The user's work hours are from 9am to 5pm in their local timezone.\n",
        ),
    )
    prompt_str = "".join(
        (
            "CONTEXT:\n",
            baseline_context,
            "- You will be given a list of calendar events for the user and a list of all invitees and their events.\n",
            "\n",
            "CORE OBJECTIVE:\n",
            f"- Reschedule one or more events on {user.given_name}'s calendar to minimize gaps between consecutive events.\n",
            f"- Create the most efficient, back-to-back schedule as possible for {user.given_name}.\n",
            "- Avoid rescheduling events that cause conflicts with other user's events.\n",
            "\n",
            "RULES: (All of these rules MUST be followed.)\n",
            f"- You MUST reschedule at least one event on {user.given_name}'s calendar.\n",
            f"- You MUST only reschedule events owned by {user.given_name}.\n",
            "- A rescheduled event MUST NOT conflict with any unchanged event on the user's calendar.\n",
            "- A rescheduled event MUST NOT conflict with any event on any other user's calendar.\n",
            "- A rescheduled event MUST have its start and end times within the user's work hours.\n",
            "- The rescheduled event MUST be scheduled for the same day as the original event.\n",
            "- DO NOT reschedule an event if it does not need to be rescheduled.\n",
            "- Events must maintain their original duration.\n",
            "- Events cannot be split or merged.\n",
            "- When rescheduling an event, you MUST choose a completely different start and end time for the event.\n",
            "\n",
            "PRIORITIES (in order of importance):\n",
            "- Minimize the amount of unscheduled time between events.\n",
            "- Minimize the number of events that need to be rescheduled.\n",
            "- Events later in the day should be rescheduled to be earlier in the day.\n",
            "\n",
            "SAFETY CHECKS (if any fail, you MUST generate new rescheduling proposals):\n",
            f"- Verify the reschedule event exists on {user.given_name}'s calendar.\n",
            "- Verify the rescheduled event does not create any new conflicts.\n",
            f"- Verify {user.given_name} is the owner of ALL rescheduled events.\n",
            "- Ensure all invitees remain available at new times.\n",
            "\n",
            "--------------------------------",
            "\n",
            f"{user.given_name}'s events to potentially reschedule:\n",
            f"{''.join(serialize_event(event) for event in users_events)}",
            "\n",
            "--------------------------------",
            "\n",
            "OTHER USER'S CONFLICTS (MUST NOT BE RESCHEDULED):\n",
            "".join(
                serialize_invitee_other_events_on(date, invitee, invitees_calendar, user)
                for invitee, invitees_calendar in other_invitees
            ),
            "\n",
            "You MUST give your response now - return a list of rescheduled events.",
        ),
    )
    reasoning_response = await unstructured_llm.ainvoke(prompt_str)
    reasoning = "".join(
        (
            "CONTEXT:\n",
            baseline_context,
            "CORE OBJECTIVE:\n",
            "- Format the given response into a valid ReschedulingProposal object.",
            "\n",
            "RULES:\n",
            "- You MUST return a valid response in the proper JSON format.",
            "- You MUST localize all times to the user's timezone.",
            "\n",
            "RESPONSE:\n",
            cast("str", reasoning_response.content),
        ),
    )
    rescheduling_proposal = await structured_llm.ainvoke(reasoning)

    if isinstance(rescheduling_proposal, ReschedulingProposal):
        rescheduled_events = []
        for event_rescheduling_proposal in rescheduling_proposal.events:
            # Filter out events that are not owned by the user
            event = next(
                filter(lambda event: str(event_rescheduling_proposal.event_id) in str(event.id), users_events),
            )  # TODO this is messy
            rescheduled_events.append(
                PendingRescheduledEvent(
                    original_event=event,
                    new_start_time=event_rescheduling_proposal.new_start_time,
                    new_end_time=event_rescheduling_proposal.new_end_time,
                    explanation=event_rescheduling_proposal.explanation,
                ),
            )
        return rescheduled_events

    msg = f"Response is not a ReschedulingProposal object: {rescheduling_proposal}"
    raise TypeError(msg)


async def apply_rescheduling_proposals(
    rescheduling_proposals: list[AcceptedRescheduledEvent],
    calendar: Calendar,
) -> None:
    for rescheduling_proposal in rescheduling_proposals:
        await calendar.change_event_time(
            rescheduling_proposal.original_event.id,
            rescheduling_proposal.new_start_time,
            rescheduling_proposal.new_end_time,
        )
