from typing import Literal, NotRequired, TypedDict

from pydantic import BaseModel, Field

from src.graph.nodes.get_rescheduling_proposals.types import GetReschedulingProposalsResponse
from src.graph.nodes.load_calendar.types import LoadCalendarResponse
from src.graph.nodes.load_invitees.types import LoadInviteesResponse
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.types import (
    AnalyzeMessageResponse,
    ReceiveMessageResponse,
    SendMessageResponse,
)
from src.types.loading import LoadingIndicator


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


GraphUpdate = (
    dict[Literal["$.load_user"], None]
    | dict[Literal["$.introduction"], None]
    | dict[Literal["$.confirm_start"], None]
    | dict[Literal["$.load_calendar"], LoadCalendarResponse]
    | dict[Literal["$.summarize_calendar"], None]
    | dict[Literal["$.load_invitees"], LoadInviteesResponse]
    | dict[Literal["$.before_rescheduling_proposals"], None]
    | dict[Literal["$.get_rescheduling_proposals"], GetReschedulingProposalsResponse]
    | dict[Literal["$.confirm_rescheduling_proposals"], None]
    | dict[Literal["$.invoke_send_rescheduling_proposal_to_invitee"], None]  # TODO
    | dict[Literal["$.conclusion"], None]
)

SubgraphUpdate = (
    dict[Literal["$.invoke_send_rescheduling_proposal_to_invitee:[uuid].send_message"], SendMessageResponse]
    | dict[Literal["$.invoke_send_rescheduling_proposal_to_invitee:[uuid].receive_message"], ReceiveMessageResponse]
    | dict[Literal["$.invoke_send_rescheduling_proposal_to_invitee:[uuid].analyze_message"], AnalyzeMessageResponse]
)

# Union type for all possible stream responses
StreamResponse = StreamlinedAIMessageChunk | GraphUpdate | SubgraphUpdate | Interrupt | LoadingIndicator
