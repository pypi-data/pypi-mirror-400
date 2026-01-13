import pytest

from llm_meter import LLMMeter


@pytest.mark.asyncio
async def test_llm_meter_singleton():
    m1 = LLMMeter(storage_url="sqlite+aiosqlite:///1.db")
    m2 = LLMMeter(storage_url="sqlite+aiosqlite:///2.db")
    assert m1 is m2


@pytest.mark.asyncio
async def test_llm_meter_wrap_unsupported():
    meter = LLMMeter()
    with pytest.raises(ValueError, match="not supported"):
        meter.wrap_client({}, provider="unsupported-provider")


@pytest.mark.asyncio
async def test_llm_meter_flush_noop():
    meter = LLMMeter()
    # Should not raise
    await meter.flush_request()


@pytest.mark.asyncio
async def test_llm_meter_set_context():
    meter = LLMMeter()
    meter.set_context(user_id="test-user")
    from llm_meter.context import get_current_context

    assert get_current_context().user_id == "test-user"


@pytest.mark.asyncio
async def test_llm_meter_wrap_openai():
    from unittest.mock import MagicMock

    meter = LLMMeter()
    mock_client = MagicMock()
    # Mock chat.completions structure
    mock_client.chat.completions.create = MagicMock()

    wrapped = meter.wrap_client(mock_client, provider="openai")
    assert wrapped is mock_client
