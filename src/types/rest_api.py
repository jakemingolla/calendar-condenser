from typing import Literal, NotRequired, TypedDict

from pydantic import BaseModel, Field

from src.types.state import (
    InitialState,
    StateWithCalendar,
    StateWithCompletedReschedulingProposals,
    StateWithInvitees,
    StateWithPendingReschedulingProposals,
)


class AdditionalKwargs(TypedDict):
    """Specific additional kwargs added to the message chunk.

    @see src/callbacks/add_source_to_messages.py
    """

    source: str


class ResponseMetadata(TypedDict):
    finish_reason: NotRequired[Literal["stop"]]  # Indicates to the UI the LLM message ends


class StreamlinedAIMessageChunk(BaseModel):
    type: Literal["AIMessageChunk"] = "AIMessageChunk"
    content: str = Field(description="The content of the message chunk")
    id: str = Field(description="Chunks with the same id are part of the same message")
    additional_kwargs: AdditionalKwargs
    response_metadata: ResponseMetadata


class Interrupt(BaseModel):
    """Indicates to the UI the graph is waiting for user input."""

    type: Literal["interrupt"] = "interrupt"
    value: str = Field(description="The content of the interrupt")
    id: str = Field(description="The id of the interrupt")


class Resume(BaseModel):
    """Sent by the UI to resume the graph execution."""

    type: Literal["resume"] = "resume"
    value: str = Field(description="The content of the resume")
    id: str = Field(description="The corresponding Interrupt id")


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
