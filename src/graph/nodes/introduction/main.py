from src.agents.guide import introduction_to_user
from src.types.state import InitialState


async def introduction(state: InitialState) -> None:
    if True:
        await introduction_to_user(state.user, state.date)
