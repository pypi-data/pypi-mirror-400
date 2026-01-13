from unittest.mock import AsyncMock, MagicMock

import pytest

from llm_meter.models import LLMUsage
from llm_meter.providers.openai import OpenAIWrapper, instrument_openai_call


@pytest.mark.asyncio
async def test_openai_wrapper_async_success():
    # Mock OpenAI client structure
    mock_client = MagicMock()
    mock_create = AsyncMock()

    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 10
    mock_usage.completion_tokens = 5
    mock_usage.total_tokens = 15

    mock_response = MagicMock()
    mock_response.model = "gpt-4o"
    mock_response.usage = mock_usage
    mock_create.return_value = mock_response

    mock_client.chat.completions.create = mock_create

    callback_called = False

    async def mock_callback(usage: LLMUsage):
        nonlocal callback_called
        callback_called = True
        assert usage.model == "gpt-4o"
        assert usage.total_tokens == 15
        assert usage.status == "success"

    # Wrap the client
    OpenAIWrapper().instrument(mock_client, mock_callback)

    # Call the instrumented method
    await mock_client.chat.completions.create(model="gpt-4o", messages=[])

    assert callback_called is True


@pytest.mark.asyncio
async def test_openai_wrapper_async_error():
    mock_client = MagicMock()
    mock_create = AsyncMock()
    mock_create.side_effect = Exception("OpenAI Error")
    mock_client.chat.completions.create = mock_create

    callback_called = False

    async def mock_callback(usage: LLMUsage):
        nonlocal callback_called
        callback_called = True
        assert usage.status == "error"
        assert usage.error_message == "OpenAI Error"

    OpenAIWrapper().instrument(mock_client, mock_callback)

    with pytest.raises(Exception, match="OpenAI Error"):
        await mock_client.chat.completions.create(model="gpt-4o", messages=[])

    assert callback_called is True


def test_openai_wrapper_sync():
    mock_client = MagicMock()
    # Not a coroutine function
    mock_create = MagicMock()
    mock_create.return_value = MagicMock()
    mock_client.chat.completions.create = mock_create

    OpenAIWrapper().instrument(mock_client, AsyncMock())

    mock_client.chat.completions.create(model="gpt-4o")
    mock_create.assert_called_once()


# --- Functional tests (previously test_openai_functional.py) ---


@pytest.mark.asyncio
async def test_instrument_openai_call_success():
    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 20
    mock_usage.completion_tokens = 10
    mock_usage.total_tokens = 30

    mock_response = MagicMock()
    mock_response.model = "gpt-4o"
    mock_response.usage = mock_usage

    async def mock_func(*args, **kwargs):
        return mock_response

    callback_records = []

    async def mock_callback(usage: LLMUsage):
        callback_records.append(usage)

    # Apply decorator
    decorated = instrument_openai_call("openai", mock_callback)(mock_func)

    # Call it
    await decorated(model="gpt-4o")

    assert len(callback_records) == 1
    assert callback_records[0].total_tokens == 30
    assert callback_records[0].status == "success"


@pytest.mark.asyncio
async def test_instrument_openai_call_error():
    async def mock_func_error(*args, **kwargs):
        raise ValueError("Oops")

    callback_records = []

    async def mock_callback(usage: LLMUsage):
        callback_records.append(usage)

    decorated = instrument_openai_call("openai", mock_callback)(mock_func_error)

    with pytest.raises(ValueError, match="Oops"):
        await decorated(model="gpt-4o")

    assert len(callback_records) == 1
    assert callback_records[0].status == "error"
    assert callback_records[0].error_message == "Oops"


@pytest.mark.asyncio
async def test_instrument_openai_call_already_instrumented():
    async def mock_func(*args, **kwargs):
        return MagicMock()

    mock_func._is_instrumented = True

    # Should return original func immediately
    decorated = instrument_openai_call("openai", AsyncMock())(mock_func)
    assert decorated is mock_func
