import logging
from unittest.mock import AsyncMock, MagicMock

import pytest

from llm_meter.providers import openai
from llm_meter.providers.openai import count_tokens, instrument_openai_call


def test_count_tokens_no_tiktoken_caplog(monkeypatch, caplog):
    # Store old tiktoken
    old_tiktoken = openai.tiktoken
    openai.tiktoken = None
    try:
        with caplog.at_level(logging.WARNING):
            res = count_tokens("hello", "gpt-4")
            assert res == 0
            assert "tiktoken not installed" in caplog.text
    finally:
        openai.tiktoken = old_tiktoken


def test_count_tokens_key_error(monkeypatch):
    mock_tiktoken = MagicMock()
    mock_tiktoken.encoding_for_model.side_effect = KeyError("model not found")
    mock_encoding = MagicMock()
    mock_encoding.encode.return_value = [1, 2, 3]
    mock_tiktoken.get_encoding.return_value = mock_encoding

    old_tiktoken = openai.tiktoken
    openai.tiktoken = mock_tiktoken
    try:
        res = count_tokens("hello", "unknown-model")
        assert res == 3
        mock_tiktoken.get_encoding.assert_called_with("cl100k_base")
    finally:
        openai.tiktoken = old_tiktoken


def test_count_tokens_general_exception(monkeypatch, caplog):
    mock_tiktoken = MagicMock()
    mock_encoding = MagicMock()
    mock_encoding.encode.side_effect = Exception("encode error")
    mock_tiktoken.encoding_for_model.return_value = mock_encoding

    old_tiktoken = openai.tiktoken
    openai.tiktoken = mock_tiktoken
    try:
        with caplog.at_level(logging.DEBUG):
            res = count_tokens("hello", "gpt-4")
            assert res == 0
            assert "Error counting tokens with tiktoken: encode error" in caplog.text
    finally:
        openai.tiktoken = old_tiktoken


@pytest.mark.asyncio
async def test_instrument_openai_call_streaming():
    # Target line 151 in openai.py
    storage_callback = AsyncMock()

    async def mock_stream_func(*args, **kwargs):
        # Return an async iterator
        async def stream():
            yield MagicMock(choices=[], usage=None)

        return stream()

    decorated = instrument_openai_call("openai", storage_callback)(mock_stream_func)

    # We need to call it with stream=True
    response = await decorated(model="gpt-4o", messages=[], stream=True)

    from llm_meter.providers.openai import InstrumentedAsyncStream

    assert isinstance(response, InstrumentedAsyncStream)
