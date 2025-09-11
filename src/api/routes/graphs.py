import json
from collections.abc import AsyncGenerator, Generator
from datetime import datetime
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessageChunk
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
from langgraph.types import Interrupt as GraphInterrupt

from src.api.serializers import StateSerializer
from src.domains.user.mock_user_provider import me
from src.graph.main import InitialState, uncompiled_graph
from src.types.loading import LoadingIndicator
from src.types.rest_api import Interrupt, Resume, StreamResponse

checkpointer = InMemorySaver()

router = APIRouter()
graphs: dict[str, CompiledStateGraph[Any]] = {
    "default": uncompiled_graph.compile(checkpointer=checkpointer),
}


def serialize_messages_chunk(chunk: Any) -> Generator[str]:  # noqa: ANN401
    for message in chunk:
        if isinstance(message, AIMessageChunk):
            source = message.additional_kwargs.get("source", "")
            if "public" in source:
                yield message.model_dump_json().replace("\n", "\\n") + "\n"


def serialize_custom_chunk(chunk: Any) -> Generator[str]:  # noqa: ANN401
    if isinstance(chunk, LoadingIndicator):
        yield chunk.model_dump_json().replace("\n", "\\n") + "\n"


def serialize_updates_chunk(chunk: Any, namespace: tuple[str, ...]) -> Generator[str]:  # noqa: ANN401
    if isinstance(chunk, dict):
        interrupt = chunk.get("__interrupt__", ({},))[0]
        if interrupt and isinstance(interrupt, GraphInterrupt):
            yield (
                Interrupt(value=interrupt.value.replace("\n", "\\n"), id=interrupt.id).model_dump_json().replace("\n", "\\n")
                + "\n"
            )
        else:
            prefix = "$." if len(namespace) < 1 else "$." + ".".join(namespace) + "."
            yield StateSerializer.to_json({f"{prefix}{key}": value for key, value in chunk.items()}) + "\n"


async def invoke_graph(graph: CompiledStateGraph[Any], thread_id: UUID, resume: Resume | None = None) -> AsyncGenerator[str]:
    date = datetime(2025, 8, 11, tzinfo=ZoneInfo(me.timezone))

    if resume:
        input = Command(resume=resume.value)
    else:
        input = InitialState(date=date)

    async for namespace, mode, chunk in graph.astream(
        input=input,
        stream_mode=["messages", "updates", "custom"],
        config={"configurable": {"thread_id": str(thread_id)}},
        subgraphs=True,
    ):
        if mode == "messages":
            for line in serialize_messages_chunk(chunk):
                yield line
        elif mode == "custom":
            for line in serialize_custom_chunk(chunk):
                yield line
        elif mode == "updates":
            for line in serialize_updates_chunk(chunk, tuple(namespace)):
                yield line


@router.post(
    "/graphs/{graph_id:str}/threads/{thread_id:uuid}/stream",
    response_model=StreamResponse,
    summary="Stream graph execution results",
    description="""
    Streams the execution results from a graph, including:

    - **State updates**: Changes to the state of the graph or subgraphs
    - **AI messages**: AIMessageChunk objects containing AI-generated responses
    - **Interrupts**: Used when the graph is waiting for user input

    The response is a stream where each line contains a JSON object.
    """,
    response_description="Stream of graph execution states and AI messages",
    tags=["graphs"],
)
async def stream(graph_id: str, thread_id: UUID, resume: Resume | None = None) -> StreamingResponse:
    graph = graphs.get(graph_id)
    if graph is None:
        raise HTTPException(status_code=404, detail="Graph not found")

    return StreamingResponse(invoke_graph(graph, thread_id, resume), media_type="text/event-stream")


@router.websocket("/graphs/{graph_id:str}/threads/{thread_id:uuid}/ws")
async def websocket_stream(websocket: WebSocket, graph_id: str, thread_id: UUID) -> None:
    """WebSocket endpoint for streaming graph execution results.

    Provides the same functionality as the HTTP stream endpoint but over WebSocket:
    - **State updates**: Changes to the state of the graph or subgraphs
    - **AI messages**: AIMessageChunk objects containing AI-generated responses
    - **Interrupts**: When the graph encounters an interrupt, it will wait for a resume command
    - **Resume commands**: Client can send resume commands to continue execution

    The client can send JSON messages with type "resume" to resume execution:
    ```json
    {
        "type": "resume",
        "value": "resume_value",
        "id": "interrupt_id"
    }
    ```

    The WebSocket will remain open and can handle multiple interrupt/resume cycles
    during a single graph execution session.
    """
    await websocket.accept()

    graph = graphs.get(graph_id)
    if graph is None:
        await websocket.close(code=1008, reason="Graph not found")
        return

    try:
        # Start the graph execution
        resume: Resume | None = None

        while True:
            # Run the graph execution
            async for chunk in invoke_graph(graph, thread_id, resume):
                await websocket.send_text(chunk)

            # After graph completes, wait for resume command
            try:
                message = await websocket.receive_text()
                data = json.loads(message)

                if data.get("type") == "resume":
                    resume = Resume(
                        value=data["value"],
                        id=data["id"],
                    )
                    # Continue the loop to restart the graph with resume data
                    continue
                # Invalid message type
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "message": "Expected resume message",
                        },
                    ),
                )
                break

            except json.JSONDecodeError:
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "message": "Invalid JSON message",
                        },
                    ),
                )
                break
            except WebSocketDisconnect:
                return

    except WebSocketDisconnect:
        pass
    except Exception as e:  # noqa: BLE001
        await websocket.send_text(
            json.dumps(
                {
                    "type": "error",
                    "message": f"Graph execution error: {e!s}",
                },
            ),
        )
        await websocket.close(code=1011, reason="Internal server error")
