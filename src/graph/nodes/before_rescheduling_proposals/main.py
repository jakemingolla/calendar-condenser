from src.agents.guide import anticipate_rescheduling_proposals
from src.types.state import StateWithInvitees


async def before_rescheduling_proposals(state: StateWithInvitees) -> None:
    if False:
        await anticipate_rescheduling_proposals(state)
