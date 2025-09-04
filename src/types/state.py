from datetime import datetime

from src.graph.nodes.get_rescheduling_proposals.types import GetReschedulingProposalsResponse
from src.graph.nodes.load_calendar.types import LoadCalendarResponse
from src.graph.nodes.load_invitees.types import LoadInviteesResponse
from src.graph.nodes.load_user.types import LoadUserResponse
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.types import InvokeSendReschedulingProposalResponse
from src.types.higher_order import BrandedBaseModel


class InitialState(BrandedBaseModel):
    date: datetime


class StateWithUser(InitialState, LoadUserResponse):
    pass


class StateWithCalendar(StateWithUser, LoadCalendarResponse):
    pass


class StateWithInvitees(StateWithCalendar, LoadInviteesResponse):
    pass


class StateWithPendingReschedulingProposals(StateWithInvitees, GetReschedulingProposalsResponse):
    pass


class StateWithInviteeMessages(StateWithPendingReschedulingProposals, InvokeSendReschedulingProposalResponse):
    pass
