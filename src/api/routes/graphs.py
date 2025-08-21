from asyncio import sleep
from collections.abc import AsyncGenerator
from datetime import datetime
from random import random
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessageChunk
from langgraph.graph.state import CompiledStateGraph

from src.api.serializers import StateSerializer
from src.domains.mock_user.mock_user_provider import me
from src.graph.main import InitialState, compiled_graph

router = APIRouter()
graphs = {
    "default": compiled_graph,
}


async def invoke_graph(graph: CompiledStateGraph[Any]) -> AsyncGenerator[str, Any]:
    date = datetime(2025, 8, 11, tzinfo=ZoneInfo(me.timezone))

    async for mode, chunk in graph.astream(
        input=InitialState(date=date, user=me),
        stream_mode=["values", "messages"],
    ):
        if mode == "values":
            yield StateSerializer.to_json(chunk) + "\n"
        elif mode == "messages":
            await sleep(random() / 10)
            for message in chunk:
                if isinstance(message, AIMessageChunk):
                    source = message.additional_kwargs.get("source", "")
                    if "public" in source:
                        yield message.model_dump_json() + "\n"


@router.post("/graphs/{graph_id:str}/stream")
async def stream(graph_id: str) -> StreamingResponse:
    graph = graphs.get(graph_id)
    if graph is None:
        raise HTTPException(status_code=404, detail="Graph not found")

    return StreamingResponse(invoke_graph(graph))
