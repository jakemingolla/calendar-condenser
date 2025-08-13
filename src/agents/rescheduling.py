from collections.abc import Sequence
from datetime import datetime

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from src.types.calendar import Calendar
from src.types.calendar_event import CalendarEvent, CalendarEventId
from src.types.rescheduled_event import PendingRescheduledEvent
from src.types.user import User


class EventReschedulingProposal(BaseModel):
    new_start_time: datetime
    new_end_time: datetime
    explanation: str


class ReschedulingProposal(BaseModel):
    events: dict[CalendarEventId, EventReschedulingProposal] = Field(
        description="A mapping of event IDs to rescheduling proposals.",
    )


llm = ChatOpenAI(model="gpt-4o-mini")
structured_llm = llm.with_structured_output(ReschedulingProposal, method="json_schema")


def serialize_event(event: CalendarEvent) -> str:
    s = f"""
Event ID: {str(event.id)[:8]}
Start time: {event.start_time.strftime("%Y-%m-%d %H:%M")}
End time: {event.end_time.strftime("%Y-%m-%d %H:%M")}
Title: {event.title}
Description: {event.description}
Owner's User ID: {str(event.owner)[:8]}
"""
    if len(event.invitees) > 0:
        s += f"Invitee IDs: {', '.join(str(invitee.id)[:8] for invitee in event.invitees)}\n"
    else:
        s += "Invitee IDs: None\n"
    return s


def serialize_invitee_other_events_on(date: datetime, invitee: User, calendar: Calendar, subject: User) -> str:
    invitees_events = calendar.get_events_on(date)
    invitees_events_not_owned_by_subject = list(
        filter(lambda event: event.owner != subject.id, invitees_events),
    )
    s = f"{invitee.given_name} (User ID: {str(invitee.id)[:8]})"
    if len(invitees_events_not_owned_by_subject) == 0:
        return f"{s} has no other events scheduled on {date.strftime('%Y-%m-%d')}.\n"
    return f"{s} has these additional events scheduled on {date.strftime('%Y-%m-%d')}:\n" + "\n".join(
        serialize_event(event) for event in invitees_events_not_owned_by_subject
    )


async def generate_rescheduling_proposals(
    date: datetime,
    user: User,
    users_calendar: Calendar,
    other_invitees: Sequence[tuple[User, Calendar]],
) -> list[PendingRescheduledEvent]:
    """Generate a rescheduling proposal for a calendar event."""
    users_events = users_calendar.get_events_on(date)
    prompt_str = "".join(
        (
            "CONTEXT:\n",
            "- You are an assistant that can help with calendar events.\n",
            f"- The current date is {date.strftime('%Y-%m-%d')}.\n"
            f"- You are speaking with {user.given_name}. Their user ID is {str(user.id)[:8]}.\n"
            f"- The user's timezone is {user.timezone}.\n",
            "- All times mentioned are in the user's local timezone on the current date.\n",
            "- The user's work hours are from 9am to 5pm in their local timezone.\n",
            "- You will be given a list of calendar events for the user and a list of all invitees and their events.\n",
            "\n",
            "CORE OBJECTIVE:\n",
            f"- Reschedule one or more events to minimize gaps between consecutive events on {user.given_name}'s calendar.\n",
            "- Your goal is to create the most efficient, back-to-back schedule as possible while respecting all rules.\n",
            "- When rescheduling an event, you MUST choose a completelydifferent start and end time for the event.\n",
            "\n",
            "RULES: (All of these rules MUST be followed.)\n",
            f"- You MUST reschedule at least one event on {user.given_name}'s calendar.\n",
            "- A rescheduled event MUST NOT conflict with any unchanged event on the user's calendar.\n",
            "- A rescheduled event MUST NOT conflict with any event on any other user's calendar.\n",
            "- An event owned by another person MUST NOT be rescheduled.\n",
            "- A rescheduled event MUST have its start and end times within the user's work hours.\n",
            "- The rescheduled event MUST be scheduled for the same day as the original event.\n",
            "- DO NOT reschedule an event if it does not need to be rescheduled.\n",
            "- Events must maintain their original duration.\n",
            "- Events cannot be split or merged.\n",
            "\n",
            "PRIORITIES (in order of importance):\n",
            "- Minimize the amount of unscheduled time between events.\n",
            "- Minimize the number of events that need to be rescheduled.\n",
            "- Events later in the day should be rescheduled to be earlier in the day.\n",
            "SAFETY CHECKS (performed after determining each rescheduled event):\n",
            "- Verify the rescheduled event does not create any new conflicts.\n",
            "- Ensure all invitees remain available at new times.\n",
            "\n",
            f"{user.given_name}'s events to potentially reschedule:\n",
            f"{''.join(serialize_event(event) for event in users_events)}",
            "\n",
            "\n".join(
                serialize_invitee_other_events_on(date, invitee, invitees_calendar, user)
                for invitee, invitees_calendar in other_invitees
            ),
            "\n",
            "You MUST give your response now - return a list of rescheduled events.",
        ),
    )
    response = await structured_llm.ainvoke(prompt_str)

    if isinstance(response, ReschedulingProposal):
        rescheduled_events = []
        for event_id, event_rescheduling_proposal in response.events.items():
            event = next(filter(lambda event: event.id == event_id, users_events))  # TODO this is messy
            rescheduled_events.append(
                PendingRescheduledEvent(
                    original_event=event,
                    new_start_time=event_rescheduling_proposal.new_start_time,
                    new_end_time=event_rescheduling_proposal.new_end_time,
                    explanation=event_rescheduling_proposal.explanation,
                ),
            )
        return rescheduled_events
    msg = f"Response is not a ReschedulingProposal object: {response}"
    raise TypeError(msg)
