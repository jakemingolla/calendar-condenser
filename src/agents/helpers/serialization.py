from src.domains.mock_user.mock_user_provider import user_provider
from src.types.calendar_event import CalendarEvent
from src.types.rescheduled_event import AcceptedRescheduledEvent, RejectedRescheduledEvent


def serialize_event(event: CalendarEvent, *, include_id: bool = True) -> str:
    s = f"""{f"Event ID: {event.id!s}" if include_id else ""}
Start time: {event.start_time.strftime("%Y-%m-%d %H:%M")}
End time: {event.end_time.strftime("%Y-%m-%d %H:%M")}
Title: {event.title}
Description: {event.description}
Owner: {user_provider.get_user(event.owner).given_name}
"""
    if len(event.invitees) > 0:
        s += f"Invitees: {', '.join(user_provider.get_user(invitee.id).given_name for invitee in event.invitees)}\n"
    else:
        s += "Invitees: None\n"
    return s


def serialize_rescheduling_proposal(rescheduling_proposal: AcceptedRescheduledEvent | RejectedRescheduledEvent) -> str:
    return f"""
Event ID: {rescheduling_proposal.original_event.id!s}
Title: {rescheduling_proposal.original_event.title}
Description: {rescheduling_proposal.original_event.description}
Original start time: {rescheduling_proposal.original_event.start_time.strftime("%Y-%m-%d %H:%M")}
Original end time: {rescheduling_proposal.original_event.end_time.strftime("%Y-%m-%d %H:%M")}
New start time: {rescheduling_proposal.new_start_time.strftime("%Y-%m-%d %H:%M")}
New end time: {rescheduling_proposal.new_end_time.strftime("%Y-%m-%d %H:%M")}
"""
