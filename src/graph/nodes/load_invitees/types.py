from src.types.calendar import Calendar
from src.types.nodes import NodeResponse
from src.types.user import User, UserId


class LoadInviteesResponse(NodeResponse):
    invitees: list[User]
    invitee_calendars: dict[UserId, Calendar]
