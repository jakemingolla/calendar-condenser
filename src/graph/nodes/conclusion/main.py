from src.agents.guide import conclusion as guide_conclusion
from src.config.main import config
from src.types.state import StateAfterSendingReschedulingProposals


async def conclusion(state: StateAfterSendingReschedulingProposals) -> None:
    if config.include_llm_messages:
        await guide_conclusion(state)
