from langgraph.types import interrupt

from src.types.state import StateWithPendingReschedulingProposals


async def confirm_rescheduling_proposals(state: StateWithPendingReschedulingProposals) -> None:
    value = interrupt(
        "Do these rescheduling proposals look good?",
    )
    assert value == "CONFIRMED"  # TODO Handle other values
