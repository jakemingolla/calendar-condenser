from src.types.calendar_event import CalendarEvent


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
