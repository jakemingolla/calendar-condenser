from src.types.messaging import IncomingMessage
from src.types.nodes import NodeResponse


class ReceiveMessageResponse(NodeResponse):
    received_message: IncomingMessage
