from src.types.messaging import OutgoingMessage
from src.types.nodes import NodeResponse


class SendMessageResponse(NodeResponse):
    sent_message: OutgoingMessage
