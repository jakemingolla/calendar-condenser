from src.domains.mock_calendar.mock_calendar import my_calendar
from src.graph.nodes.load_calendar.types import LoadCalendarResponse
from src.types.state import InitialState


async def load_calendar(state: InitialState) -> LoadCalendarResponse:
    # await asyncio.sleep(2)
    return LoadCalendarResponse(calendar=my_calendar)
