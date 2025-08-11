import json
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain.load import dumps

from src.main import agent_executor

app = FastAPI()


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


async def invoke_agent(input: str) -> AsyncGenerator[str, Any]:
    async for raw in agent_executor.astream_events(
        input={"input": input},
        include_types=[
            "chat_model",
            "tool",
        ],
    ):
        yield dumps(raw) + "\n"
        continue
        event = raw["event"]
        data = raw["data"]
        yield (
            json.dumps(
                {
                    "event": event,
                    "data": dumps(data),
                },
            )
            + "\n"
        )


@app.get("/stream")
async def stream() -> StreamingResponse:
    return StreamingResponse(invoke_agent("How many events do I have today?"))
