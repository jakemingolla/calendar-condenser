from asyncio import sleep
from collections.abc import AsyncGenerator
from datetime import datetime
from random import random
from typing import Any, Literal, NotRequired, TypedDict
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessageChunk
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
from langgraph.types import Interrupt as GraphInterrupt
from pydantic import BaseModel, Field

from src.api.serializers import StateSerializer
from src.domains.mock_user.mock_user_provider import me
from src.graph.main import InitialState, uncompiled_graph
from src.types.state import (
    StateWithCalendar,
    StateWithCompletedReschedulingProposals,
    StateWithInvitees,
    StateWithPendingReschedulingProposals,
)


class AdditionalKwargs(TypedDict):
    source: str


class ResponseMetadata(TypedDict):
    finish_reason: NotRequired[Literal["stop"]]


class StreamlinedAIMessageChunk(BaseModel):
    type: Literal["AIMessageChunk"] = "AIMessageChunk"
    content: str = Field(description="The content of the message chunk")
    id: str = Field(description="Chunks with the same id are part of the same message")
    additional_kwargs: AdditionalKwargs
    response_metadata: ResponseMetadata


class Interrupt(BaseModel):
    type: Literal["interrupt"] = "interrupt"
    value: str = Field(description="The content of the interrupt")
    id: str = Field(description="The id of the interrupt")


class Resume(BaseModel):
    type: Literal["resume"] = "resume"
    value: str = Field(description="The content of the resume")
    id: str = Field(description="The corresponding Interrupt id")


checkpointer = InMemorySaver()

router = APIRouter()
graphs: dict[str, CompiledStateGraph[Any]] = {
    "default": uncompiled_graph.compile(checkpointer=checkpointer),
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
StreamResponse = StreamlinedAIMessageChunk | State | Interrupt


async def invoke_graph(graph: CompiledStateGraph[Any], thread_id: UUID, resume: Resume | None = None) -> AsyncGenerator[str]:
    date = datetime(2025, 8, 11, tzinfo=ZoneInfo(me.timezone))

    if resume:
        input = Command(resume=resume.value)
    else:
        input = InitialState(date=date, user=me)

    async for mode, chunk in graph.astream(
        input=input,
        stream_mode=["values", "messages", "updates"],
        config={"configurable": {"thread_id": str(thread_id)}},
    ):
        if mode == "values":
            yield StateSerializer.to_json(chunk) + "\n"
        elif mode == "messages":
            await sleep(random() / 10)
            for message in chunk:
                if isinstance(message, AIMessageChunk):
                    source = message.additional_kwargs.get("source", "")
                    if "public" in source:
                        yield message.model_dump_json().replace("\n", "\\n") + "\n"
        elif mode == "updates" and isinstance(chunk, dict):
            interrupt = chunk.get("__interrupt__", ({},))[0]
            if interrupt and isinstance(interrupt, GraphInterrupt):
                yield (
                    Interrupt(
                        value=interrupt.value.replace("\n", "\\n"),
                        id=interrupt.id,
                    ).model_dump_json()
                    + "\n"
                )


@router.post(
    "/graphs/{graph_id:str}/threads/{thread_id:uuid}/stream",
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
async def stream(graph_id: str, thread_id: UUID, resume: Resume | None = None) -> StreamingResponse:
    graph = graphs.get(graph_id)
    if graph is None:
        raise HTTPException(status_code=404, detail="Graph not found")

    return StreamingResponse(invoke_graph(graph, thread_id, resume))
