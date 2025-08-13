from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from src.domains.google_calendar.types.google_calendar import GoogleCalendar
from src.domains.google_calendar.types.google_calendar_event import GoogleCalendarEvent
from src.types.calendar import CalendarId
from src.types.calendar_event import CalendarEventId, CalendarEventInvitee
from src.types.user import User, UserId

my_user_id = UserId(uuid4())
me = User(id=my_user_id, given_name="Randall Kleiser", timezone="America/New_York")

adams_user_id = UserId(uuid4())
adams_user = User(id=adams_user_id, given_name="Adam Smork", timezone="America/New_York")

sallys_user_id = UserId(uuid4())
sallys_user = User(id=sallys_user_id, given_name="Sally Li", timezone="America/Los_Angeles")

pauls_user_id = UserId(uuid4())
pauls_user = User(id=pauls_user_id, given_name="Paul Smith", timezone="America/New_York")

my_calendar = GoogleCalendar(
    id=CalendarId(uuid4()),
    name="My Calendar",
    owner=my_user_id,
    events=[],
    created_at=datetime.now(tz=ZoneInfo(me.timezone)),
    updated_at=datetime.now(tz=ZoneInfo(me.timezone)),
)

my_first_event = GoogleCalendarEvent(
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

my_second_event = GoogleCalendarEvent(
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

my_calendar.add_event(my_first_event)
my_calendar.add_event(my_second_event)


adams_calendar = GoogleCalendar(
    id=CalendarId(uuid4()),
    name="Adam's Calendar",
    owner=adams_user_id,
    events=[],
    created_at=datetime.now(tz=ZoneInfo(adams_user.timezone)),
    updated_at=datetime.now(tz=ZoneInfo(adams_user.timezone)),
)

adams_event = GoogleCalendarEvent(
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

adams_calendar.add_event(adams_event)
adams_calendar.add_event(my_first_event)
adams_calendar.add_event(my_second_event)

sallys_calendar = GoogleCalendar(
    id=CalendarId(uuid4()),
    name="Sally's Calendar",
    owner=sallys_user_id,
    events=[],
    created_at=datetime.now(tz=ZoneInfo(sallys_user.timezone)),
    updated_at=datetime.now(tz=ZoneInfo(sallys_user.timezone)),
)

sallys_calendar.add_event(my_first_event)
sallys_calendar.add_event(my_second_event)
