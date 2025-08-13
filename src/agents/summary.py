from collections.abc import Sequence

from langchain_openai import ChatOpenAI

from src.types.rescheduled_event import AcceptedRescheduledEvent, RejectedRescheduledEvent

llm = ChatOpenAI(model="gpt-4o-mini")


def summarize_rescheduling_proposals(
    rescheduling_proposals: Sequence[AcceptedRescheduledEvent | RejectedRescheduledEvent],
) -> str:
    accepted_proposals = [proposal for proposal in rescheduling_proposals if isinstance(proposal, AcceptedRescheduledEvent)]
    rejected_proposals = [proposal for proposal in rescheduling_proposals if isinstance(proposal, RejectedRescheduledEvent)]

    if len(accepted_proposals) == len(rescheduling_proposals):
        return "All proposals were accepted."
    if len(rejected_proposals) == len(rescheduling_proposals):
        return "All proposals were rejected."

    return f"{len(accepted_proposals)} proposals were accepted and {len(rejected_proposals)} were rejected."
