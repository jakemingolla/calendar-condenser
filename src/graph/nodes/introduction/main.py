from src.agents.guide import introduction_to_user
from src.config.main import config
from src.types.state import StateWithUser


async def introduction(state: StateWithUser) -> None:
    if config.include_llm_messages:
        await introduction_to_user(state.user, state.date)
