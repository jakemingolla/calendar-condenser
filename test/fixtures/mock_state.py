from datetime import datetime

import pytest

from src.domains.mock_calendar.mock_calendar import my_calendar
from src.domains.mock_user.mock_user_provider import me
from src.types.state import InitialState, StateWithCalendar


@pytest.fixture
def mock_initial_state() -> InitialState:
    return InitialState(
        date=datetime.now(),
        user=me,
    )


@pytest.fixture
def mock_state_with_calendar(mock_initial_state: InitialState) -> StateWithCalendar:
    return StateWithCalendar.model_validate(dict(mock_initial_state, calendar=my_calendar))
