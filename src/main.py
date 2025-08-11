from collections.abc import Sequence
from datetime import datetime, timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

from src.domains.google_calendar.types.google_calendar import GoogleCalendar
from src.domains.google_calendar.types.google_calendar_event import GoogleCalendarEvent
from src.types.calendar import CalendarId
from src.types.calendar_event import CalendarEventId
from src.types.user import User, UserId

llm = ChatOllama(
    model="gpt-oss:20b",
    temperature=0,
    reasoning=True,
)

user_id = UserId(uuid4())
user = User(id=user_id, given_name="Randall Kleiser", timezone="America/New_York")

calendar = GoogleCalendar(
    id=CalendarId(uuid4()),
    name="My Calendar",
    owner=user_id,
    events=[],
    created_at=datetime.now(tz=ZoneInfo(user.timezone)),
    updated_at=datetime.now(tz=ZoneInfo(user.timezone)),
)

event = GoogleCalendarEvent(
    id=CalendarEventId(uuid4()),
    title="My Event",
    description="My Event Description",
    owner=user_id,
    invitees=[],
    start_time=datetime.now(tz=ZoneInfo(user.timezone)),
    end_time=datetime.now(tz=ZoneInfo(user.timezone)) + timedelta(hours=1),
    created_at=datetime.now(tz=ZoneInfo(user.timezone)),
    updated_at=datetime.now(tz=ZoneInfo(user.timezone)),
)

calendar.add_event(event)


@tool
def get_events_on_date(date: datetime) -> Sequence[GoogleCalendarEvent]:
    """Get the events on the given date."""
    print(f"Getting events on {date}")
    return calendar.get_events_on(date)


model = llm.bind_tools([get_events_on_date])

prompt_str = "".join(
    (
        f"The current date is {datetime.now(tz=ZoneInfo(user.timezone)).strftime('%Y-%m-%d')}.\n"
        f"You are speaking with {user.given_name}.\n"
        f"The user's timezone is {user.timezone}.\n",
        "You have access to the following tools:\n"
        "get_events_on_date(date: datetime) -> Sequence[GoogleCalendarEvent]:\n",
    ),
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", prompt_str),
        ("human", "How many events do I have today?"),
        ("placeholder", "{agent_scratchpad}"),
    ],
)

tools = [get_events_on_date]
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)
