from unittest.mock import AsyncMock, MagicMock

import pytest

import llm_meter.providers.openai as openai
from llm_meter.context import attribution_context
from llm_meter.providers.openai import OpenAIClientInstrumenter


class MockDelta:
    def __init__(self, content):
        self.content = content


class MockChoice:
    def __init__(self, content):
        self.delta = MockDelta(content)


class MockUsage:
    def __init__(self, prompt, completion):
        self.prompt_tokens = prompt
        self.completion_tokens = completion
        self.total_tokens = prompt + completion


class MockChunk:
    def __init__(self, content=None, usage=None):
        self.choices = [MockChoice(content)] if content else []
        self.usage = usage
        self.model = "gpt-4o"


class MockAsyncStream:
    def __init__(self, chunks):
        self.chunks = chunks

    async def __aiter__(self):
        for chunk in self.chunks:
            yield chunk


@pytest.mark.asyncio
async def test_openai_streaming_with_usage():
    # Setup mock storage callback
    storage_callback = AsyncMock()

    # Setup mock client
    client = MagicMock()
    # Mock AsyncStream from OpenAI
    chunks = [
        MockChunk(content="Hello"),
        MockChunk(content=" world"),
        MockChunk(usage=MockUsage(10, 5)),  # Last chunk with usage
    ]
    stream = MockAsyncStream(chunks)

    # Setup create method
    client.chat.completions.create = AsyncMock(return_value=stream)

    # Instrument
    OpenAIClientInstrumenter(client, storage_callback)

    # Call create with stream=True
    with attribution_context(user_id="user_123"):
        response = await client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "user", "content": "hi"}], stream=True
        )

        # Iterate through stream to trigger recording
        collected_content = ""
        async for chunk in response:
            if chunk.choices:
                collected_content += chunk.choices[0].delta.content

    assert collected_content == "Hello world"

    # Verify storage callback was called
    storage_callback.assert_called_once()
    record = storage_callback.call_args[0][0]
    assert record.user_id == "user_123"
    assert record.input_tokens == 10
    assert record.output_tokens == 5
    assert record.status == "success"


@pytest.mark.asyncio
async def test_openai_streaming_fallback_counting(monkeypatch):
    # Mock tiktoken to avoid dependency issues during test if not installed
    mock_tiktoken = MagicMock()
    mock_encoding = MagicMock()
    # Return 1 token per word for simplicity in mock
    mock_encoding.encode.side_effect = lambda x: [1] * len(x.split())
    mock_tiktoken.encoding_for_model.return_value = mock_encoding
    mock_tiktoken.get_encoding.return_value = mock_encoding

    # Store old tiktoken from module to restore later
    old_tiktoken = openai.tiktoken
    openai.tiktoken = mock_tiktoken

    try:
        storage_callback = AsyncMock()
        client = MagicMock()

        # Chunks WITHOUT usage (typical if include_usage is not set)
        chunks = [
            MockChunk(content="DeepMind is awesome"),
        ]
        stream = MockAsyncStream(chunks)
        client.chat.completions.create = AsyncMock(return_value=stream)

        OpenAIClientInstrumenter(client, storage_callback)

        with attribution_context(user_id="dev_user"):
            response = await client.chat.completions.create(
                model="gpt-4o", messages=[{"role": "user", "content": "Tell me about DeepMind"}], stream=True
            )
            async for _ in response:
                pass

        storage_callback.assert_called_once()
        record = storage_callback.call_args[0][0]
        assert record.user_id == "dev_user"
        # "Tell me about DeepMind" -> 4 words -> 4 tokens (estimated)
        # "DeepMind is awesome" -> 3 words -> 3 tokens (estimated)
        assert record.input_tokens == 4
        assert record.output_tokens == 3
        assert record.status == "success"
    finally:
        openai.tiktoken = old_tiktoken
