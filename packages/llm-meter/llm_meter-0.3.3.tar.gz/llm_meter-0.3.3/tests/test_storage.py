from llm_meter.models import LLMUsage
from llm_meter.storage.manager import StorageManager, get_storage
from llm_meter.storage.postgres import PostgresStorageManager


def test_llm_usage_repr():
    u = LLMUsage(id=1, model="gpt-4", cost_estimate=0.05)
    assert repr(u) == "<LLMUsage(id=1, model='gpt-4', cost=0.05)>"


def test_get_storage_factory():
    """Test that the factory returns the correct storage engine."""
    # Test Postgres case
    try:
        pg_storage = get_storage("postgresql://user:pass@host/db")
        assert isinstance(pg_storage, PostgresStorageManager)
    except ImportError:
        # If asyncpg is not installed, this path cannot be tested, which is acceptable.
        pass

    # Test default SQLite case
    sqlite_storage = get_storage("sqlite+aiosqlite:///./test.db")
    assert isinstance(sqlite_storage, StorageManager)


async def test_record_and_summary(storage: StorageManager):
    usage = LLMUsage(
        request_id="test-req",
        model="gpt-4o",
        provider="openai",
        input_tokens=100,
        output_tokens=200,
        total_tokens=300,
        cost_estimate=0.01,
        endpoint="/generate",
    )

    await storage.record_usage(usage)

    summary = await storage.get_usage_summary()
    assert len(summary) == 1
    assert summary[0]["model"] == "gpt-4o"
    assert summary[0]["total_tokens"] == 300
    assert summary[0]["total_cost"] == 0.01


async def test_usage_by_endpoint(storage: StorageManager):
    u1 = LLMUsage(request_id="1", endpoint="/a", model="m", provider="p", total_tokens=10, cost_estimate=0.1)
    u2 = LLMUsage(request_id="2", endpoint="/a", model="m", provider="p", total_tokens=20, cost_estimate=0.2)
    u3 = LLMUsage(request_id="3", endpoint="/b", model="m", provider="p", total_tokens=5, cost_estimate=0.05)

    await storage.record_usage(u1)
    await storage.record_usage(u2)
    await storage.record_usage(u3)

    endpoints = await storage.get_usage_by_endpoint()
    # Sort for consistent testing
    endpoints.sort(key=lambda x: str(x["endpoint"]))

    assert len(endpoints) == 2
    assert endpoints[0]["endpoint"] == "/a"
    assert endpoints[0]["total_tokens"] == 30
    assert endpoints[1]["endpoint"] == "/b"
    assert endpoints[1]["total_tokens"] == 5
