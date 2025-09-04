from src.agents.guide import anticipate_rescheduling_proposals
from src.config.main import config
from src.types.state import StateWithInvitees


async def before_rescheduling_proposals(state: StateWithInvitees) -> None:
    if config.include_llm_messages:
        await anticipate_rescheduling_proposals(state)
