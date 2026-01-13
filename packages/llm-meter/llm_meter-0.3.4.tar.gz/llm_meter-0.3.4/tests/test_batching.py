import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from llm_meter import LLMMeter
from llm_meter.models import Budget, LLMUsage
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


async def test_batching_storage_flush(mock_storage):
    LLMMeter._instance = None
    batcher = BatchingStorageManager(mock_storage, batch_size=10, flush_interval=10.0)

    usage = LLMUsage(model="gpt-4o", total_tokens=100)
    await batcher.record_usage(usage)

    assert not mock_storage.record_batch.called

    await batcher.flush()
    assert mock_storage.record_batch.called
    assert len(mock_storage.record_batch.call_args[0][0]) == 1


async def test_batching_proxy_methods(mock_storage):
    batcher = BatchingStorageManager(mock_storage)

    res1 = await batcher.get_usage_summary()
    assert res1 == [{"model": "test", "total_tokens": 10}]

    res2 = await batcher.get_usage_by_endpoint()
    assert res2 == [{"endpoint": "test", "total_cost": 0.1}]

    res3 = await batcher.get_all_usage()
    assert res3 == []


async def test_batching_no_record_batch_fallback(mock_storage):
    # Remove record_batch to test fallback
    del mock_storage.record_batch

    batcher = BatchingStorageManager(mock_storage, batch_size=2)
    usage = LLMUsage(model="gpt-4o", total_tokens=100)
    await batcher.record_usage(usage)
    await batcher.record_usage(usage)

    await batcher.flush()
    assert mock_storage.record_usage.call_count == 2


async def test_batching_flush_error_handling(mock_storage, caplog):
    mock_storage.record_batch.side_effect = Exception("DB Down")
    batcher = BatchingStorageManager(mock_storage)

    await batcher.record_usage(LLMUsage(model="test"))
    await batcher.flush()

    assert "Failed to flush batch" in caplog.text


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


# --- Budget Proxy Method Tests ---


@pytest.fixture
def mock_storage_with_budget():
    """Mock storage with budget-related methods."""
    storage = AsyncMock()
    storage.initialize = AsyncMock()
    storage.record_usage = AsyncMock()
    storage.record_batch = AsyncMock()
    storage.get_usage_summary = AsyncMock(return_value=[])
    storage.get_usage_by_endpoint = AsyncMock(return_value=[])
    storage.get_all_usage = AsyncMock(return_value=[])
    storage.close = AsyncMock()
    storage.get_budget = AsyncMock(return_value=None)
    storage.upsert_budget = AsyncMock()
    storage.delete_budget = AsyncMock()
    storage.get_all_budgets = AsyncMock(return_value=[])
    storage.get_user_usage_in_period = AsyncMock(return_value=0.0)
    return storage


async def test_batching_get_budget(mock_storage_with_budget):
    """Test that get_budget is properly proxied to base engine."""
    from llm_meter.models import Budget

    mock_storage_with_budget.get_budget.return_value = Budget(user_id="testuser", monthly_limit=100.0)

    batcher = BatchingStorageManager(mock_storage_with_budget)
    result = await batcher.get_budget("testuser")

    assert result is not None
    assert result.user_id == "testuser"
    mock_storage_with_budget.get_budget.assert_called_once_with("testuser")


async def test_batching_upsert_budget(mock_storage_with_budget):
    """Test that upsert_budget is properly proxied to base engine."""

    batcher = BatchingStorageManager(mock_storage_with_budget)
    budget = Budget(user_id="testuser", monthly_limit=100.0)
    await batcher.upsert_budget(budget)

    mock_storage_with_budget.upsert_budget.assert_called_once_with(budget)


async def test_batching_delete_budget(mock_storage_with_budget):
    """Test that delete_budget is properly proxied to base engine."""
    batcher = BatchingStorageManager(mock_storage_with_budget)
    await batcher.delete_budget("testuser")

    mock_storage_with_budget.delete_budget.assert_called_once_with("testuser")


async def test_batching_get_all_budgets(mock_storage_with_budget):
    """Test that get_all_budgets is properly proxied to base engine."""

    batcher = BatchingStorageManager(mock_storage_with_budget)
    mock_storage_with_budget.get_all_budgets.return_value = [
        Budget(user_id="user1", monthly_limit=100.0),
        Budget(user_id="user2", monthly_limit=200.0),
    ]

    result = await batcher.get_all_budgets()

    assert len(result) == 2
    mock_storage_with_budget.get_all_budgets.assert_called_once()


async def test_batching_get_user_usage_in_period(mock_storage_with_budget):
    """Test that get_user_usage_in_period is properly proxied to base engine."""

    batcher = BatchingStorageManager(mock_storage_with_budget)
    mock_storage_with_budget.get_user_usage_in_period.return_value = 50.0

    now = datetime.now(timezone.utc)
    result = await batcher.get_user_usage_in_period("testuser", now, now)

    assert result == 50.0
    mock_storage_with_budget.get_user_usage_in_period.assert_called_once_with("testuser", now, now)
