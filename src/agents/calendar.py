from collections.abc import Sequence
from datetime import datetime
from functools import cached_property
from typing import Self
from zoneinfo import ZoneInfo

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from src.domains.google_calendar.types.google_calendar import GoogleCalendar
from src.domains.google_calendar.types.google_calendar_event import GoogleCalendarEvent
from src.types.user import User


class CalendarAgent(BaseModel):
    user: User
    calendar: GoogleCalendar
    llm: ChatOllama = Field(
        default_factory=lambda: ChatOllama(model="gpt-oss:20b", temperature=0, reasoning=True),
    )

    @cached_property
    def executor(self: Self) -> AgentExecutor:
        """Get the executor for the calendar agent."""
        tools = [
            StructuredTool.from_function(self.get_events_on_date),
            StructuredTool.from_function(self.get_events_for_today),
        ]
        agent = create_tool_calling_agent(self.llm, tools, self._prompt)
        return AgentExecutor(agent=agent, tools=tools)

    @property
    def _prompt(self: Self) -> ChatPromptTemplate:
        prompt_str = "".join(
            (
                f"The current date is {datetime.now(tz=ZoneInfo(self.user.timezone)).strftime('%Y-%m-%d')}.\n"
                f"You are speaking with {self.user.given_name}.\n"
                f"The user's timezone is {self.user.timezone}.\n",
                "You have access to the following tools:\nget_events_on_date(date: datetime) -> Sequence[GoogleCalendarEvent]:\n",
            ),
        )
        return ChatPromptTemplate.from_messages(
            [
                ("system", prompt_str),
                ("placeholder", "{agent_scratchpad}"),
                ("human", "{input}"),
            ],
        )

    def get_events_on_date(self: Self, date: datetime) -> Sequence[GoogleCalendarEvent]:
        """Get the events on the given date.

        Args:
            date: The date to get the events for.

        Returns:
            A list of events on the given date.

        """
        return self.calendar.get_events_on(date)

    def get_events_for_today(self: Self) -> Sequence[GoogleCalendarEvent]:
        """Get the events for today.

        Returns:
            A list of events for today.

        """
        return self.calendar.get_events_on(datetime.now(tz=ZoneInfo(self.user.timezone)))
