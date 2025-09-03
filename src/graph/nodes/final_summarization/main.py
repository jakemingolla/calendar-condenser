from src.agents.summary import summarize_rescheduling_proposals
from src.api.serializers import StateSerializer
from src.types.state import StateWithInviteeMessages


async def final_summarization(state: StateWithInviteeMessages) -> None:
    print("final state", StateSerializer.to_json(state, indent=2))
    if False:
        summary = summarize_rescheduling_proposals(state.completed_rescheduling_proposals)
        print(summary)
