import asyncio

from src.domains.mock_user.mock_user_provider import me
from src.graph.nodes.load_user.types import LoadUserResponse
from src.types.state import InitialState
from src.utilities.loading import indicate_loading


async def load_user(state: InitialState) -> LoadUserResponse:
    indicate_loading("Loading your profile...")
    await asyncio.sleep(1.5)
    return LoadUserResponse(
        user=me,
    )
