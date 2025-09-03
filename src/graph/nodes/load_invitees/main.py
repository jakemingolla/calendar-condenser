from src.domains.mock_calendar.mock_calendar import adams_calendar, sallys_calendar
from src.domains.mock_user.mock_user_provider import adams_user, adams_user_id, sallys_user, sallys_user_id
from src.graph.nodes.load_invitees.types import LoadInviteesResponse
from src.types.state import StateWithCalendar


async def load_invitees(state: StateWithCalendar) -> LoadInviteesResponse:
    # await asyncio.sleep(2)
    return LoadInviteesResponse(
        invitees=[adams_user, sallys_user],
        invitee_calendars={adams_user_id: adams_calendar, sallys_user_id: sallys_calendar},
    )
