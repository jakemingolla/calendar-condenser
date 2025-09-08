from src.agents.guide import summarize_state_after_sending_rescheduling_proposals
from src.config.main import config
from src.types.state import StateAfterSendingReschedulingProposals


async def after_rescheduling_proposals(state: StateAfterSendingReschedulingProposals) -> None:
    if config.include_llm_messages:
        await summarize_state_after_sending_rescheduling_proposals(state)
