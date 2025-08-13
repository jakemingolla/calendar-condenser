from random import choice

from langchain_openai import ChatOpenAI

from src.types.rescheduled_event import AcceptedRescheduledEvent, PendingRescheduledEvent, RejectedRescheduledEvent
from src.types.user import User

llm = ChatOpenAI(model="gpt-4o-mini")


async def submit_rescheduling_proposal(
    user: User,
    rescheduled_event: PendingRescheduledEvent,
) -> AcceptedRescheduledEvent | RejectedRescheduledEvent:
    print(f"Submitting rescheduling proposal for {user.given_name}...")
    if choice([True, False]):  # noqa: S311
        return AcceptedRescheduledEvent(**rescheduled_event.model_dump())
    return RejectedRescheduledEvent(**rescheduled_event.model_dump())
