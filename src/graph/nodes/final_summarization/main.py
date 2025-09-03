from src.agents.summary import summarize_rescheduling_proposals
from src.types.state import StateWithInviteeMessages


async def final_summarization(state: StateWithInviteeMessages) -> None:
    if False:
        summary = summarize_rescheduling_proposals(state.completed_rescheduling_proposals)
        print(summary)
