import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from llm_meter import LLMMeter
from llm_meter.models import LLMUsage
from llm_meter.storage.batcher import BatchingStorageManager


@pytest.fixture
def mock_storage():
    storage = AsyncMock()
    storage.initialize = AsyncMock()
    storage.record_usage = AsyncMock()
    storage.record_batch = AsyncMock()
    storage.get_usage_summary = AsyncMock(return_value=[{"model": "test", "total_tokens": 10}])
    storage.get_usage_by_endpoint = AsyncMock(return_value=[{"endpoint": "test", "total_cost": 0.1}])
    storage.get_all_usage = AsyncMock(return_value=[])
    storage.close = AsyncMock()
    return storage


@pytest.mark.asyncio
async def test_batching_storage_worker(mock_storage):
    # Reset singleton for test
    LLMMeter._instance = None

    batcher = BatchingStorageManager(mock_storage, batch_size=3, flush_interval=0.1)
    await batcher.initialize()

    usage = LLMUsage(model="gpt-4o", total_tokens=100)

    # Add 2 items (less than batch_size)
    await batcher.record_usage(usage)
    await batcher.record_usage(usage)

    # Wait a bit for interval flush
    await asyncio.sleep(0.2)

    # Should have called record_batch once with 2 items
    assert mock_storage.record_batch.called
    batch = mock_storage.record_batch.call_args[0][0]
    assert len(batch) == 2

    await batcher.close()


@pytest.mark.asyncio
async def test_batching_storage_full_batch(mock_storage):
    LLMMeter._instance = None
    batcher = BatchingStorageManager(mock_storage, batch_size=2, flush_interval=1.0)
    await batcher.initialize()

    usage = LLMUsage(model="gpt-4o", total_tokens=100)

    # Add 2 items (exactly batch_size)
    await batcher.record_usage(usage)
    await batcher.record_usage(usage)

    # Wait for worker
    await asyncio.sleep(0.1)

    assert mock_storage.record_batch.called
    await batcher.close()


@pytest.mark.asyncio
async def test_batching_storage_flush(mock_storage):
    LLMMeter._instance = None
    batcher = BatchingStorageManager(mock_storage, batch_size=10, flush_interval=10.0)

    usage = LLMUsage(model="gpt-4o", total_tokens=100)
    await batcher.record_usage(usage)

    assert not mock_storage.record_batch.called

    await batcher.flush()
    assert mock_storage.record_batch.called
    assert len(mock_storage.record_batch.call_args[0][0]) == 1


@pytest.mark.asyncio
async def test_batching_proxy_methods(mock_storage):
    batcher = BatchingStorageManager(mock_storage)

    res1 = await batcher.get_usage_summary()
    assert res1 == [{"model": "test", "total_tokens": 10}]

    res2 = await batcher.get_usage_by_endpoint()
    assert res2 == [{"endpoint": "test", "total_cost": 0.1}]

    res3 = await batcher.get_all_usage()
    assert res3 == []


@pytest.mark.asyncio
async def test_batching_no_record_batch_fallback(mock_storage):
    # Remove record_batch to test fallback
    del mock_storage.record_batch

    batcher = BatchingStorageManager(mock_storage, batch_size=2)
    usage = LLMUsage(model="gpt-4o", total_tokens=100)
    await batcher.record_usage(usage)
    await batcher.record_usage(usage)

    await batcher.flush()
    assert mock_storage.record_usage.call_count == 2


@pytest.mark.asyncio
async def test_batching_flush_error_handling(mock_storage, caplog):
    mock_storage.record_batch.side_effect = Exception("DB Down")
    batcher = BatchingStorageManager(mock_storage)

    await batcher.record_usage(LLMUsage(model="test"))
    await batcher.flush()

    assert "Failed to flush batch" in caplog.text


@pytest.mark.asyncio
async def test_batching_worker_error_handling(mock_storage, caplog):
    # Force an error in the worker loop by making queue.get fail once
    batcher = BatchingStorageManager(mock_storage)

    # Mock queue.get to raise once
    original_get = batcher._queue.get
    count = 0

    async def side_effect():
        nonlocal count
        count += 1
        if count == 1:
            raise ValueError("Queue Error")
        return await original_get()

    batcher._queue.get = side_effect

    await batcher.initialize()
    await asyncio.sleep(0.1)  # Let it run and fail

    assert "Error in batch worker: Queue Error" in caplog.text

    # Should still be able to use it
    await batcher.record_usage(LLMUsage(model="test"))
    await batcher.flush()
    await batcher.close()


@pytest.mark.asyncio
async def test_llm_meter_batching_integration(mock_storage):
    LLMMeter._instance = None
    meter = LLMMeter(storage_engine=mock_storage, enable_batching=True, batch_size=2)
    await meter.initialize()

    # Wrap a fake client
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=MagicMock(model="gpt-4o", usage=MagicMock(input_tokens=10, output_tokens=10))
    )

    wrapped = meter.wrap_client(mock_client)

    await wrapped.chat.completions.create(model="gpt-4o", messages=[])

    # Should be in queue, not storage yet
    assert not mock_storage.record_usage.called
    assert not mock_storage.record_batch.called

    await meter.flush_request()
    assert mock_storage.record_batch.called

    await meter.shutdown()
