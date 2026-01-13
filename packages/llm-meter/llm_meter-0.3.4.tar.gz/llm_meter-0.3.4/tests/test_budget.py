"""Tests for budget management functionality."""

from datetime import datetime, timezone
from typing import Any

import pytest

from llm_meter.budget import BudgetManager
from llm_meter.models import Budget


class MockStorage:
    """Mock storage for testing BudgetManager."""

    def __init__(self):
        self.budgets: dict[str, Budget] = {}
        self.usage: list[dict] = []

    async def get_budget(self, user_id: str) -> Budget | None:
        return self.budgets.get(user_id)

    async def upsert_budget(self, budget: Budget) -> None:
        self.budgets[budget.user_id] = budget

    async def delete_budget(self, user_id: str) -> None:
        self.budgets.pop(user_id, None)

    async def get_all_budgets(self) -> list[Budget]:
        return list(self.budgets.values())

    async def get_user_usage_in_period(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        total = 0.0
        for record in self.usage:
            if record["user_id"] == user_id and start_date <= record["timestamp"] <= end_date:
                total += record["cost"]
        return total

    async def get_usage_summary(self) -> list[dict[str, Any]]:
        return []

    async def get_usage_by_endpoint(self) -> list[dict[str, Any]]:
        return []

    async def get_all_usage(self) -> list:
        return []

    async def initialize(self) -> None:
        pass

    async def record_usage(self, usage) -> None:
        pass

    async def record_batch(self, batch) -> None:
        pass

    async def flush(self) -> None:
        pass

    async def close(self) -> None:
        pass


@pytest.fixture
def mock_storage():
    return MockStorage()


@pytest.fixture
def budget_manager(mock_storage):
    return BudgetManager(mock_storage)


async def test_check_budget_no_budget_configured(budget_manager, mock_storage):
    """Test that requests are allowed when no budget is configured."""
    result = await budget_manager.check_budget("user_123")

    assert result.allowed is True
    assert result.current_spend == 0.0
    assert result.limit == float("inf")
    assert result.percentage_used == 0.0
    assert result.remaining_budget == float("inf")
    assert result.should_block is False
    assert result.warning is False


async def test_check_budget_under_limit(budget_manager, mock_storage):
    """Test that requests are allowed when under the budget limit."""
    # Create a budget
    budget = Budget(
        user_id="user_123",
        monthly_limit=100.0,
        blocking_enabled=True,
        warning_threshold=0.8,
    )
    await mock_storage.upsert_budget(budget)

    # Add some usage
    mock_storage.usage.append(
        {
            "user_id": "user_123",
            "timestamp": datetime.now(timezone.utc),
            "cost": 50.0,
        }
    )

    result = await budget_manager.check_budget("user_123")

    assert result.allowed is True
    assert result.current_spend == 50.0
    assert result.limit == 100.0
    assert result.percentage_used == 50.0
    assert result.remaining_budget == 50.0
    assert result.should_block is False
    assert result.warning is False


async def test_check_budget_exceeds_limit_no_blocking(budget_manager, mock_storage):
    """Test that requests are allowed when over limit but blocking is disabled."""
    budget = Budget(
        user_id="user_123",
        monthly_limit=100.0,
        blocking_enabled=False,  # No blocking
        warning_threshold=0.8,
    )
    await mock_storage.upsert_budget(budget)

    # Add usage that exceeds limit
    mock_storage.usage.append(
        {
            "user_id": "user_123",
            "timestamp": datetime.now(timezone.utc),
            "cost": 150.0,
        }
    )

    result = await budget_manager.check_budget("user_123")

    assert result.allowed is True  # Still allowed because blocking is disabled
    assert result.current_spend == 150.0
    assert result.limit == 100.0
    assert result.should_block is False


async def test_check_budget_exceeds_limit_with_blocking(budget_manager, mock_storage):
    """Test that requests are blocked when over limit and blocking is enabled."""
    budget = Budget(
        user_id="user_123",
        monthly_limit=100.0,
        blocking_enabled=True,  # Blocking enabled
        warning_threshold=0.8,
    )
    await mock_storage.upsert_budget(budget)

    # Add usage that exceeds limit
    mock_storage.usage.append(
        {
            "user_id": "user_123",
            "timestamp": datetime.now(timezone.utc),
            "cost": 150.0,
        }
    )

    result = await budget_manager.check_budget("user_123")

    assert result.allowed is False  # Blocked
    assert result.current_spend == 150.0
    assert result.limit == 100.0
    assert result.should_block is True


async def test_check_budget_warning_threshold(budget_manager, mock_storage):
    """Test that warning is triggered when approaching limit."""
    budget = Budget(
        user_id="user_123",
        monthly_limit=100.0,
        blocking_enabled=False,
        warning_threshold=0.8,  # 80% warning
    )
    await mock_storage.upsert_budget(budget)

    # Add usage at 85% of limit
    mock_storage.usage.append(
        {
            "user_id": "user_123",
            "timestamp": datetime.now(timezone.utc),
            "cost": 85.0,
        }
    )

    result = await budget_manager.check_budget("user_123")

    assert result.warning is True
    assert result.percentage_used == 85.0


async def test_check_budget_daily_limit(budget_manager, mock_storage):
    """Test that daily limit is used when set."""
    budget = Budget(
        user_id="user_123",
        monthly_limit=100.0,
        daily_limit=10.0,  # Daily limit takes precedence
        blocking_enabled=True,
        warning_threshold=0.8,
    )
    await mock_storage.upsert_budget(budget)

    # Add usage that exceeds daily limit but not monthly
    mock_storage.usage.append(
        {
            "user_id": "user_123",
            "timestamp": datetime.now(timezone.utc),
            "cost": 50.0,
        }
    )

    result = await budget_manager.check_budget("user_123")

    assert result.limit == 10.0  # Daily limit used
    assert result.current_spend == 50.0
    assert result.allowed is False  # Blocked because over daily limit


async def test_get_budget_status(budget_manager, mock_storage):
    """Test getting detailed budget status."""
    budget = Budget(
        user_id="user_123",
        monthly_limit=100.0,
        blocking_enabled=True,
        warning_threshold=0.8,
    )
    await mock_storage.upsert_budget(budget)

    mock_storage.usage.append(
        {
            "user_id": "user_123",
            "timestamp": datetime.now(timezone.utc),
            "cost": 25.0,
        }
    )

    status = await budget_manager.get_budget_status("user_123")

    assert status["user_id"] == "user_123"
    assert status["budget_configured"] is True
    assert status["limit"] == 100.0
    assert status["current_spend"] == 25.0
    assert status["percentage_used"] == 25.0
    assert status["blocking_enabled"] is True


async def test_get_budget_status_no_budget(budget_manager, mock_storage):
    """Test getting status when no budget is configured."""
    status = await budget_manager.get_budget_status("unknown_user")

    assert status["user_id"] == "unknown_user"
    assert status["budget_configured"] is False
    assert status["limit"] is None


async def test_delete_budget(mock_storage):
    """Test deleting a budget."""
    budget = Budget(user_id="user_123", monthly_limit=100.0)
    await mock_storage.upsert_budget(budget)

    assert await mock_storage.get_budget("user_123") is not None

    await mock_storage.delete_budget("user_123")

    assert await mock_storage.get_budget("user_123") is None


async def test_period_boundaries_monthly(budget_manager, mock_storage):
    """Test that monthly period boundaries are calculated correctly."""
    budget = Budget(
        user_id="user_123",
        monthly_limit=100.0,
        warning_threshold=0.8,
    )
    await mock_storage.upsert_budget(budget)

    result = await budget_manager.check_budget("user_123")

    # Period should start at the first day of the month
    assert result.period_start.day == 1
    assert result.period_start.hour == 0
    assert result.period_start.minute == 0

    # Period should end at the last day of the current month
    assert result.period_end.month == result.period_start.month
    assert result.period_end.year == result.period_start.year


async def test_period_boundaries_daily(budget_manager, mock_storage):
    """Test that daily period boundaries are calculated correctly."""
    budget = Budget(
        user_id="user_123",
        daily_limit=10.0,
        warning_threshold=0.8,
    )
    await mock_storage.upsert_budget(budget)

    result = await budget_manager.check_budget("user_123")

    # Period should start at the beginning of the day
    assert result.period_start.hour == 0
    assert result.period_start.minute == 0

    # Period should end at the end of the day
    assert result.period_end.hour == 23
    assert result.period_end.minute == 59


async def test_period_boundaries_december_edge_case(mock_storage):
    """Test that monthly period boundaries are calculated correctly in December."""

    # Create a custom get_now function that returns December 2024
    def get_december_now():
        return datetime(2024, 12, 15, 12, 0, 0, tzinfo=timezone.utc)

    # Create manager with custom get_now to simulate December
    manager = BudgetManager(mock_storage, get_now=get_december_now)
    budget = Budget(
        user_id="dec_user",
        monthly_limit=100.0,
        warning_threshold=0.8,
    )
    await mock_storage.upsert_budget(budget)

    result = await manager.check_budget("dec_user")

    # Period should start at the first day of December 2024
    assert result.period_start.month == 12
    assert result.period_start.year == 2024
    assert result.period_start.day == 1

    # Period should end at December 31, 2024 (last day of month)
    assert result.period_end.month == 12
    assert result.period_end.year == 2024
    assert result.period_end.day == 31


async def test_check_budget_budget_configured_no_limit(budget_manager, mock_storage):
    """Test that requests are allowed when budget is configured but no limit is set."""
    # Create a budget without any limit (both daily_limit and monthly_limit are None)
    budget = Budget(
        user_id="user_123",
        blocking_enabled=True,
        warning_threshold=0.8,
    )
    await mock_storage.upsert_budget(budget)

    # Add some usage
    mock_storage.usage.append(
        {
            "user_id": "user_123",
            "timestamp": datetime.now(timezone.utc),
            "cost": 50.0,
        }
    )

    result = await budget_manager.check_budget("user_123")

    assert result.allowed is True
    assert result.current_spend == 50.0
    assert result.limit == float("inf")
    assert result.percentage_used == 0.0
    assert result.remaining_budget == float("inf")
    assert result.should_block is False
    assert result.warning is False


async def test_upsert_budget_update_existing(budget_manager, mock_storage):
    """Test that upserting updates an existing budget."""
    # Create initial budget
    budget = Budget(
        user_id="user_123",
        monthly_limit=100.0,
        blocking_enabled=False,
    )
    await mock_storage.upsert_budget(budget)

    # Update budget
    updated_budget = Budget(
        user_id="user_123",
        monthly_limit=200.0,
        blocking_enabled=True,
    )
    await mock_storage.upsert_budget(updated_budget)

    # Check that budget was updated
    stored = await mock_storage.get_budget("user_123")
    assert stored is not None
    assert stored.monthly_limit == 200.0
    assert stored.blocking_enabled is True
