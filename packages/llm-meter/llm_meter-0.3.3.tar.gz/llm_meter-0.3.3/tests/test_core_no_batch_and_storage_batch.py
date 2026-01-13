import pytest

from llm_meter.core import LLMMeter
from llm_meter.models import LLMUsage
from llm_meter.storage.manager import StorageManager


@pytest.mark.asyncio
async def test_llm_meter_without_batching_uses_base_storage():
    # Ensure singleton reset
    LLMMeter._instance = None
    # Use a temporary in‑memory SQLite URL
    storage_url = "sqlite+aiosqlite:///:memory:"
    meter = LLMMeter(storage_url=storage_url, enable_batching=False)
    await meter.initialize()
    # Storage should be a plain StorageManager, not BatchingStorageManager
    assert isinstance(meter.storage, StorageManager)
    # flush_request should be a no‑op (does not raise)
    await meter.flush_request()
    await meter.shutdown()


@pytest.mark.asyncio
async def test_storage_manager_record_batch():
    # Use in‑memory SQLite for isolation
    manager = StorageManager("sqlite+aiosqlite:///:memory:")
    await manager.initialize()
    # Prepare a batch of usage records
    usages = [
        LLMUsage(
            request_id="r1",
            provider="openai",
            model="gpt-4o",
            input_tokens=5,
            output_tokens=5,
            total_tokens=10,
            cost_estimate=0.01,
            endpoint="e1",
            user_id="u1",
            feature="f1",
            job_id="j1",
            status="success",
        ),
        LLMUsage(
            request_id="r2",
            provider="openai",
            model="gpt-4o",
            input_tokens=10,
            output_tokens=10,
            total_tokens=20,
            cost_estimate=0.02,
            endpoint="e2",
            user_id="u2",
            feature="f2",
            job_id="j2",
            status="success",
        ),
    ]
    # Record the batch
    await manager.record_batch(usages)
    # Verify that both records are persisted
    all_records = await manager.get_all_usage()
    assert len(all_records) == 2
    # Ensure fields match
    ids = {rec.request_id for rec in all_records}
    assert ids == {"r1", "r2"}
    await manager.close()


@pytest.mark.asyncio
async def test_storage_manager_record_batch_empty():
    """Calling record_batch with an empty list should be a no‑op and not raise."""
    manager = StorageManager("sqlite+aiosqlite:///:memory:")
    await manager.initialize()
    await manager.record_batch([])
    all_records = await manager.get_all_usage()
    assert all_records == []
    await manager.close()
