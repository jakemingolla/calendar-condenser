from collections.abc import AsyncGenerator
from typing import Any

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain.load import dumps

from src.agents.calendar import CalendarAgent
from src.domains.mock_calendar.mock_calendar import my_calendar
from src.domains.mock_user.mock_user_provider import me

calendar_agent = CalendarAgent(user=me, calendar=my_calendar)  # type: ignore
app = FastAPI()


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


async def invoke_agent(input: str) -> AsyncGenerator[str, Any]:
    async for raw in calendar_agent.executor.astream_events(
        input={"input": input},
        include_types=[
            "chat_model",
            "tool",
        ],
    ):
        yield dumps(raw) + "\n"


@app.get("/stream")
async def stream() -> StreamingResponse:
    return StreamingResponse(invoke_agent("How many events do I have today?"))
