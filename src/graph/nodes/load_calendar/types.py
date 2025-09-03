from src.types.calendar import Calendar
from src.types.nodes import NodeResponse


class LoadCalendarResponse(NodeResponse):
    calendar: Calendar
