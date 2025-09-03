from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo

from langgraph.graph import END, START, StateGraph

from src.types.messaging import IncomingMessage, OutgoingMessage
from src.types.nodes import NodeResponse
from src.types.rescheduled_event import PendingRescheduledEvent
from src.types.state import State
from src.types.user import User

MessageAnalysis = Literal["positive", "negative", "unknown"]


class InitialState(State):
    user: User
    invitee: User
    pending_rescheduling_proposals: list[PendingRescheduledEvent]


class SendMessageResponse(NodeResponse):
    sent_message: OutgoingMessage


class ReceiveMessageResponse(NodeResponse):
    received_message: IncomingMessage


class AnalyzeMessageResponse(NodeResponse):
    message_analysis: MessageAnalysis


class StateWithSentMessage(InitialState, SendMessageResponse):
    pass


class StateWithReceivedMessage(StateWithSentMessage, ReceiveMessageResponse):
    pass


class StateWithMessageAnalysis(StateWithReceivedMessage, AnalyzeMessageResponse):
    pass


async def send_message(state: InitialState) -> SendMessageResponse:
    return SendMessageResponse(
        sent_message=OutgoingMessage(
            content="I need to reschedule this event because I have a conflict.",
            sent_at=datetime.now(ZoneInfo(state.user.timezone)),
            from_user=state.user,
            to_user=state.invitee,
        ),
    )


async def receive_message(state: StateWithSentMessage) -> ReceiveMessageResponse:
    return ReceiveMessageResponse(
        received_message=IncomingMessage(
            content="Yes, that works for me.",
            sent_at=datetime.now(ZoneInfo(state.user.timezone)),
            from_user=state.invitee,
            to_user=state.user,
        ),
    )


async def analyze_message(state: StateWithReceivedMessage) -> AnalyzeMessageResponse:
    return AnalyzeMessageResponse(
        message_analysis="positive",
    )


uncompiled_graph = StateGraph(
    state_schema=StateWithMessageAnalysis,
    input_schema=InitialState,
    output_schema=StateWithMessageAnalysis,
)
uncompiled_graph.add_node("send_message", send_message)
uncompiled_graph.add_node("receive_message", receive_message)
uncompiled_graph.add_node("analyze_message", analyze_message)

uncompiled_graph.add_edge(START, "send_message")
uncompiled_graph.add_edge("send_message", "receive_message")
uncompiled_graph.add_edge("receive_message", "analyze_message")
uncompiled_graph.add_edge("analyze_message", END)
