from src.types.state import InitialState, StateWithCalendar


def test_initial_state_type(mock_initial_state: InitialState) -> None:
    assert mock_initial_state.type == "InitialState"


def test_subsequent_state_type(mock_state_with_calendar: StateWithCalendar) -> None:
    assert mock_state_with_calendar.type == "StateWithCalendar"
