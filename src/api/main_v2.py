from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from src.api.serializers import StateSerializer
from src.domains.mock_user.mock_user_provider import me
from src.graph.main import InitialState, compiled_graph

app = FastAPI()


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


async def invoke_graph() -> AsyncGenerator[str, Any]:
    date = datetime(2025, 8, 11, tzinfo=ZoneInfo(me.timezone))

    async for _, chunk in compiled_graph.astream(
        input=InitialState(date=date, user=me),
        stream_mode=["values"],
    ):
        yield StateSerializer.to_json(chunk) + "\n"


@app.post("/")
async def invoke_agent() -> StreamingResponse:
    return StreamingResponse(invoke_graph())
