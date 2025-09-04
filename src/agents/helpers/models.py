from langchain_openai import ChatOpenAI

from src.callbacks.add_source_to_messages import AddSourceToMessagesCallback
from src.config.main import config


def get_llm(source: str, model: str = "gpt-4o-mini") -> ChatOpenAI:
    return ChatOpenAI(model=model, api_key=config.openai_api_key, callbacks=[AddSourceToMessagesCallback(source=source)])
