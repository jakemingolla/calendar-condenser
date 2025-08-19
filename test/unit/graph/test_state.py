import pytest
from pydantic import ValidationError

from src.domains.mock_calendar.mock_calendar import my_calendar
from src.graph.state import InitialState, StateWithCalendar


def test_initial_state_type(mock_initial_state: InitialState) -> None:
    assert mock_initial_state.type == "InitialState"


def test_subsequent_state_type(mock_state_with_calendar: StateWithCalendar) -> None:
    assert mock_state_with_calendar.type == "StateWithCalendar"


def test_from_previous_state(mock_initial_state: InitialState) -> None:
    updated_state = StateWithCalendar.from_previous_state(mock_initial_state, calendar=my_calendar)
    assert updated_state.calendar == my_calendar
    assert updated_state.date == mock_initial_state.date
    assert updated_state.user == mock_initial_state.user


def test_from_previous_state_with_extra_fields(mock_initial_state: InitialState) -> None:
    with pytest.raises(ValidationError):
        StateWithCalendar.from_previous_state(mock_initial_state, calendar=my_calendar, extra_field="extra_value")
