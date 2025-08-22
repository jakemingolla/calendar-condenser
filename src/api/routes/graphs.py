from asyncio import sleep
from collections.abc import AsyncGenerator
from datetime import datetime
from random import random
from typing import Any, Literal, TypedDict
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessageChunk
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field

from src.api.serializers import StateSerializer
from src.domains.mock_user.mock_user_provider import me
from src.graph.main import InitialState, compiled_graph
from src.types.state import (
    StateWithCalendar,
    StateWithCompletedReschedulingProposals,
    StateWithInvitees,
    StateWithPendingReschedulingProposals,
)


class AdditionalKwargs(TypedDict):
    source: str


class StreamlinedAIMessageChunk(BaseModel):
    type: Literal["AIMessageChunk"] = "AIMessageChunk"
    content: str = Field(description="The content of the message chunk")
    id: str = Field(description="Chunks with the same id are part of the same message")
    additional_kwargs: AdditionalKwargs


router = APIRouter()
graphs = {
    "default": compiled_graph,
}

# Union type for all possible state types that can be returned from the graph
State = (
    InitialState
    | StateWithCalendar
    | StateWithInvitees
    | StateWithPendingReschedulingProposals
    | StateWithCompletedReschedulingProposals
)

# Union type for all possible stream responses
StreamResponse = StreamlinedAIMessageChunk | State


async def invoke_graph(graph: CompiledStateGraph[Any]) -> AsyncGenerator[str]:
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


@router.post(
    "/graphs/{graph_id:str}/stream",
    response_model=StreamResponse,
    summary="Stream graph execution results",
    description="""
    Streams the execution results from a graph, including:

    - **State updates**: Various state objects (InitialState, StateWithCalendar, etc.)
      that show the progression through the graph execution
    - **AI messages**: AIMessageChunk objects containing AI-generated responses

    The response is a stream where each line contains a JSON object.
    """,
    response_description="Stream of graph execution states and AI messages",
    tags=["graphs"],
)
async def stream(graph_id: str) -> StreamingResponse:
    graph = graphs.get(graph_id)
    if graph is None:
        raise HTTPException(status_code=404, detail="Graph not found")

    return StreamingResponse(invoke_graph(graph))
