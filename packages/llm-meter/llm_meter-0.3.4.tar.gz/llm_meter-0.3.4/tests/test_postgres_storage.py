import importlib
import sys
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from testcontainers.postgres import PostgresContainer

import llm_meter.storage.postgres
from llm_meter.models import LLMUsage
from llm_meter.storage.postgres import PostgresStorageManager, asyncpg


@pytest.fixture
async def pg_storage():
    """Fixture to create a Postgres container and a storage manager for it."""
    with PostgresContainer("postgres:16-alpine") as pg:
        dsn = pg.get_connection_url(driver="asyncpg").replace("postgresql+asyncpg", "postgresql")
        storage = PostgresStorageManager(dsn=dsn)
        await storage.initialize()
        yield storage
        await storage.close()


async def test_postgres_initialize(pg_storage: PostgresStorageManager):
    """Test that the table is created on initialization."""
    assert pg_storage._pool is not None
    async with pg_storage._pool.acquire() as conn:
        result = await conn.fetchval("SELECT to_regclass('llm_usage')")
        assert result == "llm_usage"


async def test_postgres_initialize_already_initialized(pg_storage: PostgresStorageManager):
    """Test that calling initialize again is a no-op."""
    old_pool = pg_storage._pool
    await pg_storage.initialize()
    assert pg_storage._pool is old_pool


async def test_postgres_initialize_failure(caplog):
    """Test that a failure during pool creation is logged and raised."""
    from unittest.mock import patch

    with patch("llm_meter.storage.postgres.asyncpg.create_pool", side_effect=Exception("Connection refused")):
        storage = PostgresStorageManager(dsn="postgresql://user:pass@host:5432/db")
        with pytest.raises(Exception, match="Connection refused"):
            await storage.initialize()
        assert "Failed to initialize PostgresStorageManager: Connection refused" in caplog.text


async def test_postgres_record_and_get_all(pg_storage: PostgresStorageManager):
    """Test recording and retrieving a single usage record."""
    usage = LLMUsage(
        request_id="req_123",
        model="gpt-4o",
        provider="openai",
        total_tokens=150,
        cost_estimate=0.001,
        timestamp=datetime.now(timezone.utc),
    )
    await pg_storage.record_usage(usage)
    all_usage = await pg_storage.get_all_usage()
    assert len(all_usage) == 1
    retrieved = all_usage[0]
    assert retrieved.request_id == "req_123"
    assert retrieved.total_tokens == 150


async def test_postgres_record_batch(pg_storage: PostgresStorageManager):
    """Test recording a batch of usage records."""
    records = [
        LLMUsage(request_id="req_1", model="model1"),
        LLMUsage(request_id="req_2", model="model2"),
    ]
    await pg_storage.record_batch(records)
    all_usage = await pg_storage.get_all_usage()
    assert len(all_usage) == 2


async def test_postgres_record_empty_batch(pg_storage: PostgresStorageManager):
    """Test that recording an empty batch is a no-op."""
    await pg_storage.record_batch([])
    all_usage = await pg_storage.get_all_usage()
    assert len(all_usage) == 0


async def test_postgres_record_batch_failure(caplog):
    """Test that a failure during batch recording is logged."""
    mock_conn = AsyncMock()
    mock_conn.executemany.side_effect = Exception("DB write error")

    # Create a proper async context manager by creating a class that implements the protocol
    class AsyncContextManager:
        async def __aenter__(self):
            return mock_conn

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return None

    # Create a mock pool where acquire() is a coroutine that returns the context manager
    def mock_acquire():
        return AsyncContextManager()

    mock_pool = AsyncMock()
    mock_pool.acquire = MagicMock(side_effect=mock_acquire)
    storage = PostgresStorageManager(pool=mock_pool)
    await storage.record_batch([LLMUsage(request_id="req_1", model="model1")])
    assert "Failed to record batch to PostgreSQL: DB write error" in caplog.text


async def test_postgres_get_usage_summary(pg_storage: PostgresStorageManager):
    """Test the aggregation of usage summary."""
    records = [
        LLMUsage(provider="openai", model="gpt-4", total_tokens=100, cost_estimate=0.1, latency_ms=100),
        LLMUsage(provider="openai", model="gpt-4", total_tokens=200, cost_estimate=0.2, latency_ms=200),
    ]
    await pg_storage.record_batch(records)
    summary = await pg_storage.get_usage_summary()
    assert len(summary) == 1
    openai_summary = summary[0]
    assert openai_summary["call_count"] == 2
    assert openai_summary["total_tokens"] == 300
    assert openai_summary["total_cost"] == pytest.approx(0.3)
    assert openai_summary["avg_latency_ms"] == pytest.approx(150)


async def test_postgres_get_usage_by_endpoint(pg_storage: PostgresStorageManager):
    """Test the aggregation of usage by endpoint."""
    records = [
        LLMUsage(endpoint="/chat", total_tokens=10, cost_estimate=0.01),
        LLMUsage(endpoint="/chat", total_tokens=15, cost_estimate=0.015),
    ]
    await pg_storage.record_batch(records)
    by_endpoint = await pg_storage.get_usage_by_endpoint()
    assert len(by_endpoint) == 1
    chat_endpoint = by_endpoint[0]
    assert chat_endpoint["call_count"] == 2
    assert chat_endpoint["total_tokens"] == 25


async def test_postgres_flush_noop(pg_storage: PostgresStorageManager):
    """Test that flush is a no-op and doesn't raise."""
    await pg_storage.flush()


async def test_postgres_import_error():
    """Test that an ImportError is raised if asyncpg is not installed."""
    original_asyncpg = asyncpg
    try:
        sys.modules["asyncpg"] = None
        importlib.reload(llm_meter.storage.postgres)
        with pytest.raises(ImportError, match="PostgreSQL support requires 'asyncpg'"):
            llm_meter.storage.postgres.PostgresStorageManager(dsn="dummy_dsn")
    finally:
        sys.modules["asyncpg"] = original_asyncpg
        importlib.reload(llm_meter.storage.postgres)


def test_postgres_init_no_args():
    """Test that creating a manager with no dsn or pool raises ValueError."""
    with pytest.raises(ValueError, match="Either 'dsn' or 'pool' must be provided"):
        PostgresStorageManager()


async def test_initialize_with_injected_pool():
    """Test that initialize works correctly when a pool is injected."""
    mock_conn = AsyncMock()

    # Create a proper async context manager by creating a class that implements the protocol
    class AsyncContextManager:
        async def __aenter__(self):
            return mock_conn

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return None

    # Create a mock pool where acquire() is a coroutine that returns the context manager
    def mock_acquire():
        return AsyncContextManager()

    mock_pool = AsyncMock()
    mock_pool.acquire = MagicMock(side_effect=mock_acquire)
    storage = PostgresStorageManager(pool=mock_pool)
    await storage.initialize()
    # Should create both llm_usage and budgets tables
    assert mock_conn.execute.call_count == 2
    calls = mock_conn.execute.call_args_list
    assert "CREATE TABLE IF NOT EXISTS llm_usage" in calls[0][0][0]
    assert "CREATE TABLE IF NOT EXISTS budgets" in calls[1][0][0]


async def test_postgres_get_methods_uninitialized():
    """Test that get_* methods on an uninitialized storage return empty lists."""
    storage = PostgresStorageManager(dsn="postgresql://fake")
    assert await storage.get_all_usage() == []
    assert await storage.get_usage_summary() == []
    assert await storage.get_usage_by_endpoint() == []


# --- Budget Method Tests ---


async def test_postgres_budget_crud(pg_storage: PostgresStorageManager):
    """Test CRUD operations for budgets."""

    from llm_meter.models import Budget

    # Create a budget
    budget = Budget(
        user_id="test_user",
        monthly_limit=100.0,
        daily_limit=10.0,
        blocking_enabled=True,
        warning_threshold=0.8,
    )
    await pg_storage.upsert_budget(budget)

    # Read it back
    retrieved = await pg_storage.get_budget("test_user")
    assert retrieved is not None
    assert retrieved.monthly_limit == 100.0
    assert retrieved.daily_limit == 10.0
    assert retrieved.blocking_enabled is True
    assert retrieved.warning_threshold == 0.8


async def test_postgres_budget_update(pg_storage: PostgresStorageManager):
    """Test updating an existing budget."""
    from llm_meter.models import Budget

    # Create initial budget
    await pg_storage.upsert_budget(Budget(user_id="update_user", monthly_limit=50.0))

    # Update it
    updated = Budget(
        user_id="update_user",
        monthly_limit=200.0,
        daily_limit=20.0,
        blocking_enabled=True,
        warning_threshold=0.5,
    )
    await pg_storage.upsert_budget(updated)

    # Verify update
    retrieved = await pg_storage.get_budget("update_user")
    assert retrieved is not None
    assert retrieved.monthly_limit == 200.0
    assert retrieved.daily_limit == 20.0
    assert retrieved.warning_threshold == 0.5


async def test_postgres_get_user_usage_in_period(pg_storage: PostgresStorageManager):
    """Test getting user usage in a time period."""
    from datetime import datetime, timedelta, timezone

    # Record usage
    now = datetime.now(timezone.utc)
    usage1 = LLMUsage(
        request_id="p1",
        user_id="period_user",
        model="gpt-4",
        provider="openai",
        total_tokens=100,
        cost_estimate=0.5,
        timestamp=now,
    )
    usage2 = LLMUsage(
        request_id="p2",
        user_id="period_user",
        model="gpt-4",
        provider="openai",
        total_tokens=200,
        cost_estimate=1.0,
        timestamp=now - timedelta(hours=1),
    )
    await pg_storage.record_batch([usage1, usage2])

    # Get usage for period
    start = now - timedelta(hours=2)
    end = now + timedelta(hours=1)
    total = await pg_storage.get_user_usage_in_period("period_user", start, end)

    assert total == 1.5


async def test_postgres_delete_budget(pg_storage: PostgresStorageManager):
    """Test deleting a budget."""
    from llm_meter.models import Budget

    # Create a budget
    await pg_storage.upsert_budget(Budget(user_id="delete_user", monthly_limit=100.0))

    # Verify exists
    assert await pg_storage.get_budget("delete_user") is not None

    # Delete it
    await pg_storage.delete_budget("delete_user")

    # Verify deleted
    assert await pg_storage.get_budget("delete_user") is None


async def test_postgres_get_all_budgets(pg_storage: PostgresStorageManager):
    """Test getting all budgets."""
    from llm_meter.models import Budget

    # Create multiple budgets
    await pg_storage.upsert_budget(Budget(user_id="pg_user1", monthly_limit=100.0))
    await pg_storage.upsert_budget(Budget(user_id="pg_user2", monthly_limit=200.0))
    await pg_storage.upsert_budget(Budget(user_id="pg_user3", monthly_limit=300.0))

    budgets = await pg_storage.get_all_budgets()

    assert len(budgets) == 3
    user_ids = [b.user_id for b in budgets]
    assert "pg_user1" in user_ids
    assert "pg_user2" in user_ids
    assert "pg_user3" in user_ids


async def test_postgres_budget_not_found(pg_storage: PostgresStorageManager):
    """Test getting a budget that doesn't exist."""
    result = await pg_storage.get_budget("nonexistent")
    assert result is None


async def test_postgres_delete_nonexistent_budget(pg_storage: PostgresStorageManager):
    """Test deleting a nonexistent budget doesn't error."""
    await pg_storage.delete_budget("nonexistent")  # Should not raise
