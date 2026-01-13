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


# --- Budget Tests for StorageManager ---


async def test_upsert_budget_new(storage: StorageManager):
    """Test creating a new budget."""
    from llm_meter.models import Budget

    budget = Budget(
        user_id="new_user",
        monthly_limit=100.0,
        daily_limit=10.0,
        blocking_enabled=True,
        warning_threshold=0.8,
    )
    await storage.upsert_budget(budget)

    # Verify it was created
    retrieved = await storage.get_budget("new_user")
    assert retrieved is not None
    assert retrieved.monthly_limit == 100.0
    assert retrieved.daily_limit == 10.0
    assert retrieved.blocking_enabled is True


async def test_upsert_budget_update_existing(storage: StorageManager):
    """Test updating an existing budget (covers lines 124-127)."""
    from llm_meter.models import Budget

    # First create a budget
    original = Budget(
        user_id="existing_user",
        monthly_limit=50.0,
        daily_limit=5.0,
        blocking_enabled=False,
        warning_threshold=0.9,
    )
    await storage.upsert_budget(original)

    # Now update it
    updated = Budget(
        user_id="existing_user",
        monthly_limit=200.0,
        daily_limit=20.0,
        blocking_enabled=True,
        warning_threshold=0.7,
    )
    await storage.upsert_budget(updated)

    # Verify it was updated
    retrieved = await storage.get_budget("existing_user")
    assert retrieved is not None
    assert retrieved.monthly_limit == 200.0
    assert retrieved.daily_limit == 20.0
    assert retrieved.blocking_enabled is True
    assert retrieved.warning_threshold == 0.7


async def test_delete_budget(storage: StorageManager):
    """Test deleting a budget."""
    from llm_meter.models import Budget

    # First create a budget
    budget = Budget(user_id="to_delete", monthly_limit=100.0)
    await storage.upsert_budget(budget)

    # Verify it exists
    assert await storage.get_budget("to_delete") is not None

    # Delete it
    await storage.delete_budget("to_delete")

    # Verify it's gone
    assert await storage.get_budget("to_delete") is None


async def test_get_all_budgets(storage: StorageManager):
    """Test getting all budgets."""
    from llm_meter.models import Budget

    # Create multiple budgets
    await storage.upsert_budget(Budget(user_id="user1", monthly_limit=100.0))
    await storage.upsert_budget(Budget(user_id="user2", monthly_limit=200.0))
    await storage.upsert_budget(Budget(user_id="user3", monthly_limit=300.0))

    budgets = await storage.get_all_budgets()

    assert len(budgets) == 3
    user_ids = [b.user_id for b in budgets]
    assert "user1" in user_ids
    assert "user2" in user_ids
    assert "user3" in user_ids


async def test_get_user_usage_in_period(storage: StorageManager):
    """Test getting user usage in a time period."""
    from datetime import datetime, timedelta, timezone

    from llm_meter.models import Budget

    # Create a budget for the user
    await storage.upsert_budget(Budget(user_id="period_user", monthly_limit=100.0))

    # Record some usage
    now = datetime.now(timezone.utc)
    usage1 = LLMUsage(
        request_id="u1",
        user_id="period_user",
        model="gpt-4",
        provider="openai",
        total_tokens=100,
        cost_estimate=0.5,
        timestamp=now,
    )
    usage2 = LLMUsage(
        request_id="u2",
        user_id="period_user",
        model="gpt-4",
        provider="openai",
        total_tokens=200,
        cost_estimate=1.0,
        timestamp=now - timedelta(hours=1),
    )
    await storage.record_usage(usage1)
    await storage.record_usage(usage2)

    # Get usage for the period
    start = now - timedelta(hours=2)
    end = now + timedelta(hours=1)
    total = await storage.get_user_usage_in_period("period_user", start, end)

    assert total == 1.5  # 0.5 + 1.0
