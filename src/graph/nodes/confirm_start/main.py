from langgraph.types import interrupt

from src.types.state import InitialState


async def confirm_start(state: InitialState) -> None:
    value = interrupt(
        "Do you want to start the rescheduling process?",
    )
    assert value == "CONFIRMED"  # TODO Handle other values
