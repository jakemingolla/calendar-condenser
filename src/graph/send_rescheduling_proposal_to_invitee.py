from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo

from langgraph.graph import END, START, StateGraph

from src.types.messaging import IncomingMessage, OutgoingMessage
from src.types.rescheduled_event import PendingRescheduledEvent
from src.types.state import State
from src.types.user import User

MessageAnalysis = Literal["positive", "negative", "unknown"]


class InitialState(State):
    user: User
    invitee: User
    pending_rescheduling_proposals: list[PendingRescheduledEvent]


class StateWithSentMessage(InitialState):
    sent_message: OutgoingMessage


class StateWithReceivedMessage(StateWithSentMessage):
    received_message: IncomingMessage


class StateWithMessageAnalysis(StateWithReceivedMessage):
    message_analysis: MessageAnalysis


async def send_message(state: InitialState) -> StateWithSentMessage:
    return StateWithSentMessage.from_previous_state(
        state,
        sent_message=OutgoingMessage(
            content="I need to reschedule this event because I have a conflict.",
            sent_at=datetime.now(ZoneInfo(state.user.timezone)),
            from_user=state.user,
            to_user=state.invitee,
        ),
    )


async def receive_message(state: StateWithSentMessage) -> StateWithReceivedMessage:
    return StateWithReceivedMessage.from_previous_state(
        state,
        received_message=IncomingMessage(
            content="Yes, that works for me.",
            sent_at=datetime.now(ZoneInfo(state.user.timezone)),
            from_user=state.invitee,
            to_user=state.user,
        ),
    )


async def analyze_message(state: StateWithReceivedMessage) -> StateWithMessageAnalysis:
    return StateWithMessageAnalysis.from_previous_state(
        state,
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
