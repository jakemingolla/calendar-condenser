from enum import StrEnum
from typing import cast

from pydantic import BaseModel, Field

from src.agents.helpers.models import get_llm
from src.domains.messaging.mock_messaging_platform import MockMessagingPlatform
from src.types.rescheduled_event import AcceptedRescheduledEvent, PendingRescheduledEvent, RejectedRescheduledEvent

messaging_platform = MockMessagingPlatform()


class ReschedulingProposalResolution(StrEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


# The LLM cannot directly return an enum value, so we wrap it in a Pydantic model.
class ReschedulingProposalResolutionOutput(BaseModel):
    resolution: ReschedulingProposalResolution
    reason: str = Field(description="The reason for the resolution.")


structured_llm = get_llm(source="messaging.structured_output").with_structured_output(
    ReschedulingProposalResolutionOutput,
)

unstructured_llm = get_llm(source="messaging.private")


async def determine_rescheduling_proposal_resolution(
    rescheduling_proposal: PendingRescheduledEvent,
    message: str,
    response: str,
) -> AcceptedRescheduledEvent | RejectedRescheduledEvent:
    prompt = "".join(
        (
            "CONTEXT:\n",
            "- A user has been given a proposal reschedule an event on their calendar.\n",
            "- The user was told the following message:\n",
            f"{message}\n",
            "- The user responded with the following message:\n",
            f"{response}\n",
            "\n",
            "CORE OBJECTIVE:\n",
            "- Determine whether the user accepted or rejected the rescheduling proposal.\n",
            "\n",
            "RULES:\n",
            "- You MUST respond with a valid enum value.\n",
            "- If you cannot determine whether the user accepted the rescheduling proposal, consider it rejected.\n",
            "- You MUST provide a short sentence for the reason why you made your decision.\n",
        ),
    )
    reasoning_response = await unstructured_llm.ainvoke(prompt)
    reasoning = cast("str", reasoning_response.content)
    output = await structured_llm.ainvoke(reasoning)

    if isinstance(output, ReschedulingProposalResolutionOutput):
        if output.resolution == ReschedulingProposalResolution.ACCEPTED:
            return AcceptedRescheduledEvent(**rescheduling_proposal.model_dump())
        return RejectedRescheduledEvent(**rescheduling_proposal.model_dump())
    msg = f"Unknown rescheduling proposal resolution: {output}"
    raise ValueError(msg)
