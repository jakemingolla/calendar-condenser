from datetime import datetime

import pytest

from src.domains.mock_calendar.mock_calendar import my_calendar
from src.domains.mock_user.mock_user_provider import me
from src.types.state import InitialState, StateWithCalendar, StateWithUser


@pytest.fixture
def mock_initial_state() -> InitialState:
    return InitialState(
        date=datetime.now(),
    )


@pytest.fixture
def mock_state_with_user(mock_initial_state: InitialState) -> StateWithUser:
    return StateWithUser.model_validate(dict(mock_initial_state, user=me))


@pytest.fixture
def mock_state_with_calendar(mock_state_with_user: StateWithUser) -> StateWithCalendar:
    return StateWithCalendar.model_validate(dict(mock_state_with_user, calendar=my_calendar))
