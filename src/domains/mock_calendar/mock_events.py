from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from src.domains.mock_user.mock_user_provider import (
    adams_user,
    adams_user_id,
    me,
    my_user_id,
    pauls_user_id,
    sallys_user,
    sallys_user_id,
)
from src.types.calendar_event import CalendarEvent, CalendarEventId, CalendarEventInvitee

my_first_event = CalendarEvent(
    id=CalendarEventId(uuid4()),
    title="Chimera Brainstorming",
    description="We will be brainstorming ideas for a new product.",
    owner=my_user_id,
    invitees=[
        CalendarEventInvitee(id=adams_user_id, confirmed=True),
        CalendarEventInvitee(id=sallys_user_id, confirmed=True),
    ],
    start_time=datetime(2025, 8, 11, 9, 0, 0, tzinfo=ZoneInfo(me.timezone)),
    end_time=datetime(2025, 8, 11, 10, 0, 0, tzinfo=ZoneInfo(me.timezone)),
    created_at=datetime.now(tz=ZoneInfo(me.timezone)),
    updated_at=datetime.now(tz=ZoneInfo(me.timezone)),
)

my_second_event = CalendarEvent(
    id=CalendarEventId(uuid4()),
    title="Team Chimera Grooming",
    description="We will be grooming upcoming work for the next sprint.",
    owner=my_user_id,
    invitees=[
        CalendarEventInvitee(id=adams_user_id, confirmed=True),
        CalendarEventInvitee(id=sallys_user_id, confirmed=True),
    ],
    start_time=datetime(2025, 8, 11, 13, 0, 0, tzinfo=ZoneInfo(me.timezone)),
    end_time=datetime(2025, 8, 11, 14, 0, 0, tzinfo=ZoneInfo(me.timezone)),
    created_at=datetime.now(tz=ZoneInfo(me.timezone)),
    updated_at=datetime.now(tz=ZoneInfo(me.timezone)),
)


adams_event = CalendarEvent(
    id=CalendarEventId(uuid4()),
    title="Private Meeting",
    description="Adam will be meeting with his manager to discuss his performance.",
    owner=adams_user_id,
    invitees=[
        CalendarEventInvitee(id=pauls_user_id, confirmed=True),
    ],
    start_time=datetime(2025, 8, 11, 10, 0, 0, tzinfo=ZoneInfo(adams_user.timezone)),
    end_time=datetime(2025, 8, 11, 12, 0, 0, tzinfo=ZoneInfo(adams_user.timezone)),
    created_at=datetime.now(tz=ZoneInfo(adams_user.timezone)),
    updated_at=datetime.now(tz=ZoneInfo(adams_user.timezone)),
)

sallys_event = CalendarEvent(
    id=CalendarEventId(uuid4()),
    title="Customer Call (Anthem Health)",
    description="We will be calling a customer to discuss their needs.",
    owner=sallys_user_id,
    invitees=[],
    start_time=datetime(2025, 8, 11, 11, 0, 0, tzinfo=ZoneInfo(sallys_user.timezone)),
    end_time=datetime(2025, 8, 11, 12, 0, 0, tzinfo=ZoneInfo(sallys_user.timezone)),
    created_at=datetime.now(tz=ZoneInfo(sallys_user.timezone)),
    updated_at=datetime.now(tz=ZoneInfo(sallys_user.timezone)),
)
