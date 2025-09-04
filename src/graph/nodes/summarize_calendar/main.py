from src.agents.guide import summarize_state_with_calendar
from src.config.main import config
from src.types.state import StateWithCalendar


async def summarize_calendar(state: StateWithCalendar) -> None:
    if config.include_llm_messages:
        await summarize_state_with_calendar(state)
