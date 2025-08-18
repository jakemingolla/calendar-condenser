"""LangChain callback to add source information to message chunks."""

from typing import Any

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatGenerationChunk


class AddSourceToMessagesCallback(BaseCallbackHandler):
    """Callback that adds a 'source' additional_kwarg to all message chunks.

    This callback can be used to track the source of generated tokens,
    which is useful for debugging, logging, or routing purposes.
    """

    def __init__(self, source: str):
        """Initialize the callback with a source identifier.

        Args:
            source: The source identifier to add to all message chunks

        """
        super().__init__()
        self.source = source

    def on_llm_new_token(
        self,
        token: str,
        chunk: dict[str, Any] | BaseMessage | None = None,
        run_id: str | None = None,
        parent_run_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Add source information to each token chunk.

        Args:
            token: The new token being generated
            chunk: The chunk containing the token
            run_id: The ID of the current run
            parent_run_id: The ID of the parent run
            **kwargs: Additional keyword arguments

        """
        # Handle different chunk types
        if chunk is None:
            return

        if isinstance(chunk, ChatGenerationChunk):
            chunk.message.additional_kwargs["source"] = self.source
            return

    @property
    def always_verbose(self) -> bool:
        """Return True to ensure this callback is always called."""
        return True
