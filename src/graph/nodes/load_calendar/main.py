import asyncio

from src.config.main import config
from src.domains.mock_calendar.mock_calendar import my_calendar
from src.graph.nodes.load_calendar.types import LoadCalendarResponse
from src.types.state import InitialState
from src.utilities.loading import indicate_loading


async def load_calendar(state: InitialState) -> LoadCalendarResponse:
    indicate_loading("Loading your calendar...")
    await asyncio.sleep(config.delay_seconds_load_calendar)
    return LoadCalendarResponse(calendar=my_calendar)
