from typing import Annotated

from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.analyze_message.types import AnalyzeMessageResponse
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.receive_message.types import ReceiveMessageResponse
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.send_message.types import SendMessageResponse
from src.types.higher_order import BrandedBaseModel
from src.types.messaging import IncomingMessage, OutgoingMessage
from src.types.nodes import NodeResponse
from src.types.rescheduled_event import PendingRescheduledEvent
from src.types.user import User, UserId
from src.utilities.merge_dicts import merge_dicts


class InitialState(BrandedBaseModel):
    user: User
    invitee: User
    pending_rescheduling_proposals: list[PendingRescheduledEvent]


class StateWithSentMessage(InitialState, SendMessageResponse):
    pass


class StateWithReceivedMessage(StateWithSentMessage, ReceiveMessageResponse):
    pass


class StateWithMessageAnalysis(StateWithReceivedMessage, AnalyzeMessageResponse):
    pass


class InvokeSendReschedulingProposalResponse(NodeResponse):
    conversations_by_invitee: Annotated[dict[UserId, list[IncomingMessage | OutgoingMessage]], merge_dicts]
