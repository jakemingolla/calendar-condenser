from src.api.serializers import StateSerializer
from src.config.main import config
from src.types.state import StateWithInviteeMessages


async def final_summarization(state: StateWithInviteeMessages) -> None:
    print("final state", StateSerializer.to_json(state, indent=2))
    if config.include_llm_messages:
        # TODO: implement
        pass
