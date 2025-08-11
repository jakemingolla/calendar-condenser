import asyncio
from collections.abc import Sequence
from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from src.graph.mock_data import adams_calendar, adams_user, me, my_calendar, sallys_calendar, sallys_user
from src.types.calendar import CalendarEvent
from src.types.user import User, UserId


class RescheduledEvent(BaseModel):
    event_id: str
    new_start_time: datetime
    new_end_time: datetime
    explanation: str = Field(description="A detailed explanation of the rescheduling proposal.")


llm = ChatOllama(model="llama3.1")
structured_llm = llm.with_structured_output(RescheduledEvent, method="json_schema")


def serialize_event(event: CalendarEvent) -> str:
    return f"""
{event.start_time.hour} - {event.end_time.hour}: {str(event.id)[:8]}
{event.title}
{event.description}
"""


def serialize_invitee_and_their_events(invitee: UserId, events: Sequence[CalendarEvent]) -> str:
    return f"""
{str(invitee)[:8]}'s events:
{"\n".join(serialize_event(event) for event in events)}
"""


async def generate_rescheduling_proposal(
    user: User,
    events: Sequence[CalendarEvent],
    invitees_and_their_events: Sequence[tuple[UserId, Sequence[CalendarEvent]]],
) -> RescheduledEvent:
    """Generate a rescheduling proposal for a calendar event."""
    prompt_str = "".join(
        (
            "CONTEXT:\n",
            "You are an assistant that can help with calendar events.\n",
            f"The current date is {datetime.now(tz=ZoneInfo(user.timezone)).strftime('%Y-%m-%d')}.\n"
            f"You are speaking with {user.given_name}.\n"
            f"The user's timezone is {user.timezone}.\n",
            "The user's work hours are from 9am to 5pm in their local timezone.\n",
            "You will be given a list of calendar events for the user and a list of all invitees and their events.\n",
            "TASK:\n"
            "Reschedule one or more events to make the user's schedule as uninterrupted as possible.\n"
            "RULES:\n"
            "- A rescheduled event MUST NOT overlap with any existing event.\n",
            "- A time for a rescheduled event MUST NOT conflict with any other event for any invitee.\n"
            "- The rescheduled event MUST be scheduled for the same day as the original event.\n"
            "- DO NOT reschedule an event if it does not need to be rescheduled.\n"
            "PRIORITIES (in order of importance):\n"
            "- Minimize the number of events that need to be rescheduled.\n"
            "- Minimize the amount of unscheduled time between events.\n"
            "- Events later in the day should be rescheduled to be earlier in the day.\n"
            "EVENTS:\n",
            f"{'\n'.join(serialize_event(event) for event in events)}\n",
            "INVITEES AND THEIR EVENTS:\n",
            f"{'\n'.join(serialize_invitee_and_their_events(invitee, events) for invitee, events in invitees_and_their_events)}\n",
        ),
    )
    response = await structured_llm.ainvoke(prompt_str)
    return RescheduledEvent.model_validate(response)


async def main() -> None:
    events = my_calendar.events
    invitees_and_their_events = [
        (adams_user.id, adams_calendar.events),
        (sallys_user.id, sallys_calendar.events),
    ]
    rescheduling_proposal = await generate_rescheduling_proposal(me, events, invitees_and_their_events)

    print("My calendar events:")
    for event in events:
        print(f"{event.start_time.hour} - {event.end_time.hour}: {str(event.id)[:8]}")
    for invitee, invitee_events in invitees_and_their_events:
        print()
        print(f"{str(invitee)[:8]}'s calendar events:")
        for event in invitee_events:
            print(f"{event.start_time.hour} - {event.end_time.hour}: {str(event.id)[:8]}")
    print()
    print("Rescheduling proposal")
    print("Event ID:", str(rescheduling_proposal.event_id)[:8])
    print("New start time:", rescheduling_proposal.new_start_time.hour)
    print("New end time:", rescheduling_proposal.new_end_time.hour)
    print("Explanation:", rescheduling_proposal.explanation)


if __name__ == "__main__":
    asyncio.run(main())
