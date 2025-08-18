from asyncio import sleep
from enum import StrEnum

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from src.domains.mock_messaging.mock_messaging_platform import MockMessagingPlatform
from src.types.rescheduled_event import AcceptedRescheduledEvent, PendingRescheduledEvent, RejectedRescheduledEvent
from src.types.user import User

llm = ChatOpenAI(model="gpt-4o-mini")

messaging_platform = MockMessagingPlatform()


async def generate_rescheduling_proposal_message(
    rescheduling_proposal: PendingRescheduledEvent,
) -> str:
    return (
        "I'm proposing to reschedule the event from "
        f"{rescheduling_proposal.new_start_time} to {rescheduling_proposal.new_end_time}."
    )


class ReschedulingProposalResolution(StrEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


# The LLM cannot directly return an enum value, so we wrap it in a Pydantic model.
class ReschedulingProposalResolutionOutput(BaseModel):
    resolution: ReschedulingProposalResolution
    reason: str = Field(description="The reason for the resolution.")


resolution_llm = llm.with_structured_output(
    ReschedulingProposalResolutionOutput,
)


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
    output = await resolution_llm.ainvoke(prompt)

    if isinstance(output, ReschedulingProposalResolutionOutput):
        if output.resolution == ReschedulingProposalResolution.ACCEPTED:
            return AcceptedRescheduledEvent(**rescheduling_proposal.model_dump())
        return RejectedRescheduledEvent(**rescheduling_proposal.model_dump())
    msg = f"Unknown rescheduling proposal resolution: {output}"
    raise ValueError(msg)


# TODO better word for submit?
async def submit_rescheduling_proposal(
    user: User,
    rescheduled_event: PendingRescheduledEvent,
) -> AcceptedRescheduledEvent | RejectedRescheduledEvent:
    message = await generate_rescheduling_proposal_message(rescheduled_event)
    receipt = await messaging_platform.send_message(user, message)
    response: str | None = None

    while response is None:
        response = await messaging_platform.get_message_response(receipt)
        print(f"Still waiting for a response from {user.given_name}...")
        await sleep(1)

    print(f"{user.given_name} responded with: {response}")
    return await determine_rescheduling_proposal_resolution(rescheduled_event, message, response)
