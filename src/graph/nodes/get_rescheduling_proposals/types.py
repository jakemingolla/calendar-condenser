from src.types.nodes import NodeResponse
from src.types.rescheduled_event import PendingRescheduledEvent


class GetReschedulingProposalsResponse(NodeResponse):
    pending_rescheduling_proposals: list[PendingRescheduledEvent]
