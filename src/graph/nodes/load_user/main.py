from src.domains.mock_user.mock_user_provider import me
from src.graph.nodes.load_user.types import LoadUserResponse
from src.types.state import StateWithCalendar


async def load_user(state: StateWithCalendar) -> LoadUserResponse:
    # await asyncio.sleep(2)
    return LoadUserResponse(
        user=me,
    )
