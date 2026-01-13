from unittest.mock import AsyncMock, MagicMock

import pytest

from llm_meter.context import attribution_context
from llm_meter.providers.anthropic import AnthropicWrapper


class MockUsage:
    def __init__(self, input_tokens, output_tokens):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class MockMessage:
    def __init__(self, model, input_tokens, output_tokens):
        self.model = model
        self.usage = MockUsage(input_tokens, output_tokens)


class MockEvent:
    def __init__(self, type, message=None, usage=None):
        self.type = type
        self.message = message
        self.usage = usage


@pytest.mark.asyncio
async def test_anthropic_async_success():
    storage_callback = AsyncMock()
    client = MagicMock()

    mock_response = MockMessage("claude-3-5-sonnet", 10, 20)
    client.messages.create = AsyncMock(return_value=mock_response)

    # Instrument
    AnthropicWrapper().instrument(client, storage_callback)

    with attribution_context(user_id="anthropic_user"):
        response = await client.messages.create(
            model="claude-3-5-sonnet", messages=[{"role": "user", "content": "hi"}], stream=False
        )

    assert response.model == "claude-3-5-sonnet"
    storage_callback.assert_called_once()
    record = storage_callback.call_args[0][0]
    assert record.provider == "anthropic"
    assert record.input_tokens == 10
    assert record.output_tokens == 20
    assert record.user_id == "anthropic_user"


@pytest.mark.asyncio
async def test_anthropic_streaming_success():
    storage_callback = AsyncMock()
    client = MagicMock()

    class MockAsyncStream:
        def __init__(self, events):
            self.events = events

        async def __aiter__(self):
            for e in self.events:
                yield e

    events = [
        MockEvent("message_start", message=MockMessage("claude-3-5-sonnet", 5, 0)),
        MockEvent("message_delta", usage=MockUsage(5, 15)),
        MockEvent("message_stop"),
    ]
    client.messages.create = AsyncMock(return_value=MockAsyncStream(events))

    AnthropicWrapper().instrument(client, storage_callback)

    with attribution_context(job_id="job_1"):
        response = await client.messages.create(
            model="claude-3-5-sonnet", messages=[{"role": "user", "content": "hi"}], stream=True
        )
        async for _ in response:
            pass

    storage_callback.assert_called_once()
    record = storage_callback.call_args[0][0]
    assert record.input_tokens == 5
    assert record.output_tokens == 15
    assert record.job_id == "job_1"
    assert record.status == "success"


@pytest.mark.asyncio
async def test_anthropic_error():
    storage_callback = AsyncMock()
    client = MagicMock()
    client.messages.create = AsyncMock(side_effect=ValueError("Anthropic Down"))

    AnthropicWrapper().instrument(client, storage_callback)

    with pytest.raises(ValueError, match="Anthropic Down"):
        await client.messages.create(model="claude-3-opus")

    storage_callback.assert_called_once()
    record = storage_callback.call_args[0][0]
    assert record.status == "error"
    assert record.error_message == "Anthropic Down"


def test_anthropic_sync_success():
    storage_callback = AsyncMock()
    client = MagicMock()

    mock_response = MockMessage("claude-3-haiku", 5, 5)
    # Not a coroutine function
    client.messages.create = MagicMock(return_value=mock_response)

    # Instrument
    AnthropicWrapper().instrument(client, storage_callback)

    response = client.messages.create(model="claude-3-haiku")
    assert response.model == "claude-3-haiku"
    # Current sync wrap doesn't record (matches openai.py pattern for v1)
