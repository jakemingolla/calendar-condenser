from src.types.calendar_event import CalendarEvent
from src.types.rescheduled_event import AcceptedRescheduledEvent, RejectedRescheduledEvent


def serialize_event(event: CalendarEvent) -> str:
    s = f"""
Event ID: {event.id!s}
Start time: {event.start_time.strftime("%Y-%m-%d %H:%M")}
End time: {event.end_time.strftime("%Y-%m-%d %H:%M")}
Title: {event.title}
Description: {event.description}
Owner's User ID: {event.owner!s}
"""
    if len(event.invitees) > 0:
        s += f"Invitee IDs: {', '.join(str(invitee.id) for invitee in event.invitees)}\n"
    else:
        s += "Invitee IDs: None\n"
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
