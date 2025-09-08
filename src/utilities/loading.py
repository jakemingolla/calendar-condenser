from langgraph.config import get_stream_writer

from src.types.loading import LoadingIndicator


def indicate_loading(message: str) -> None:
    writer = get_stream_writer()
    writer(LoadingIndicator(message=message))
