"""Unit tests for AddSourceToMessagesCallback."""

from langchain_core.messages import AIMessageChunk, HumanMessage
from langchain_core.outputs import ChatGenerationChunk

from src.callbacks.add_source_to_messages import AddSourceToMessagesCallback


def test_init():
    """Test callback initialization."""
    source = "test_source"
    callback = AddSourceToMessagesCallback(source)

    assert callback.source == source
    assert callback.always_verbose is True


def test_init_with_empty_source():
    """Test callback initialization with empty source."""
    source = ""
    callback = AddSourceToMessagesCallback(source)

    assert callback.source == source


def test_on_llm_new_token_with_chat_generation_chunk():
    """Test on_llm_new_token with ChatGenerationChunk."""
    source = "test_source"
    callback = AddSourceToMessagesCallback(source)

    # Create a proper AIMessageChunk with additional_kwargs
    message = AIMessageChunk(content="test", additional_kwargs={})

    # Create a ChatGenerationChunk
    chunk = ChatGenerationChunk(message=message)

    # Call the method
    callback.on_llm_new_token(
        token="test_token",
        chunk=chunk,  # type: ignore
        run_id="test_run_id",
        parent_run_id="test_parent_run_id",
    )

    # Verify source was added to additional_kwargs
    assert message.additional_kwargs["source"] == source


def test_on_llm_new_token_with_dict_chunk():
    """Test on_llm_new_token with dict chunk (should not modify)."""
    source = "test_source"
    callback = AddSourceToMessagesCallback(source)

    # Create a dict chunk
    chunk = {"message": "test_message"}

    # Call the method
    callback.on_llm_new_token(
        token="test_token",
        chunk=chunk,
        run_id="test_run_id",
        parent_run_id="test_parent_run_id",
    )

    # Verify chunk was not modified
    assert chunk == {"message": "test_message"}


def test_on_llm_new_token_with_base_message_chunk():
    """Test on_llm_new_token with BaseMessage chunk (should not modify)."""
    source = "test_source"
    callback = AddSourceToMessagesCallback(source)

    # Create a BaseMessage chunk
    chunk = HumanMessage(content="test_message")

    # Call the method
    callback.on_llm_new_token(
        token="test_token",
        chunk=chunk,
        run_id="test_run_id",
        parent_run_id="test_parent_run_id",
    )

    # Verify chunk was not modified
    assert chunk.content == "test_message"


def test_on_llm_new_token_with_none_chunk():
    """Test on_llm_new_token with None chunk."""
    source = "test_source"
    callback = AddSourceToMessagesCallback(source)

    # Call the method with None chunk
    callback.on_llm_new_token(
        token="test_token",
        chunk=None,
        run_id="test_run_id",
        parent_run_id="test_parent_run_id",
    )

    # Should not raise any errors


def test_on_llm_new_token_with_existing_source():
    """Test on_llm_new_token when source already exists in additional_kwargs."""
    source = "test_source"
    callback = AddSourceToMessagesCallback(source)

    # Create a proper AIMessageChunk with existing additional_kwargs
    message = AIMessageChunk(
        content="test",
        additional_kwargs={"source": "existing_source", "other": "value"},
    )

    # Create a ChatGenerationChunk
    chunk = ChatGenerationChunk(message=message)

    # Call the method
    callback.on_llm_new_token(
        token="test_token",
        chunk=chunk,  # type: ignore
    )

    # Verify source was overwritten
    assert message.additional_kwargs["source"] == source
    assert message.additional_kwargs["other"] == "value"


def test_on_llm_new_token_with_additional_kwargs_empty():
    """Test on_llm_new_token when additional_kwargs is empty dict."""
    source = "test_source"
    callback = AddSourceToMessagesCallback(source)

    # Create a proper AIMessageChunk with empty additional_kwargs
    message = AIMessageChunk(content="test", additional_kwargs={})

    # Create a ChatGenerationChunk
    chunk = ChatGenerationChunk(message=message)

    # Call the method
    callback.on_llm_new_token(
        token="test_token",
        chunk=chunk,  # type: ignore
    )

    # Verify source was added
    assert message.additional_kwargs["source"] == source


def test_on_llm_new_token_with_minimal_parameters():
    """Test on_llm_new_token with minimal required parameters."""
    source = "test_source"
    callback = AddSourceToMessagesCallback(source)

    # Create a proper AIMessageChunk
    message = AIMessageChunk(content="test", additional_kwargs={})

    # Create a ChatGenerationChunk
    chunk = ChatGenerationChunk(message=message)

    # Call the method with only required parameters
    callback.on_llm_new_token("test_token", chunk)  # type: ignore

    # Verify source was added
    assert message.additional_kwargs["source"] == source


def test_on_llm_new_token_with_extra_kwargs():
    """Test on_llm_new_token with extra keyword arguments."""
    source = "test_source"
    callback = AddSourceToMessagesCallback(source)

    # Create a proper AIMessageChunk
    message = AIMessageChunk(content="test", additional_kwargs={})

    # Create a ChatGenerationChunk
    chunk = ChatGenerationChunk(message=message)

    # Call the method with extra kwargs
    callback.on_llm_new_token(
        token="test_token",
        chunk=chunk,  # type: ignore
        extra_param="extra_value",
        another_param=123,
    )

    # Verify source was added
    assert message.additional_kwargs["source"] == source


def test_always_verbose_property():
    """Test that always_verbose property returns True."""
    callback = AddSourceToMessagesCallback("test_source")
    assert callback.always_verbose is True


def test_multiple_instances_different_sources():
    """Test that multiple instances can have different sources."""
    source1 = "source_1"
    source2 = "source_2"

    callback1 = AddSourceToMessagesCallback(source1)
    callback2 = AddSourceToMessagesCallback(source2)

    assert callback1.source == source1
    assert callback2.source == source2
    assert callback1.source != callback2.source


def test_source_with_special_characters():
    """Test callback with source containing special characters."""
    source = "test@source.com/123!@#$%^&*()"
    callback = AddSourceToMessagesCallback(source)

    assert callback.source == source


def test_source_with_unicode():
    """Test callback with unicode source."""
    source = "测试源_unicode_source_🎉"
    callback = AddSourceToMessagesCallback(source)

    assert callback.source == source
