"""Budget management service for tracking and checking user budgets."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from llm_meter.models import Budget
from llm_meter.storage.base import StorageEngine

# Type alias for datetime factory function
DateTimeFactory = Callable[[], datetime]


@dataclass
class BudgetCheckResult:
    """Result of a budget check."""

    allowed: bool
    current_spend: float
    limit: float
    percentage_used: float
    remaining_budget: float
    should_block: bool
    period_start: datetime
    period_end: datetime
    warning: bool


class BudgetManager:
    """
    Service for checking and managing user budgets.

    Args:
        storage: The storage engine for budget data
        get_now: Optional callable that returns current UTC datetime.
                 Defaults to datetime.now(timezone.utc). Useful for testing.
    """

    def __init__(
        self,
        storage: StorageEngine,
        get_now: DateTimeFactory | None = None,
    ) -> None:
        self.storage = storage
        self._get_now = get_now or (lambda: datetime.now(timezone.utc))

    async def check_budget(self, user_id: str) -> BudgetCheckResult:
        """
        Check if a user can make an LLM call based on their budget.
        """
        budget = await self.storage.get_budget(user_id)

        if budget is None:
            # No budget configured - allow all requests
            return BudgetCheckResult(
                allowed=True,
                current_spend=0.0,
                limit=float("inf"),
                percentage_used=0.0,
                remaining_budget=float("inf"),
                should_block=False,
                period_start=datetime.now(timezone.utc),
                period_end=datetime.now(timezone.utc),
                warning=False,
            )

        # Calculate period boundaries
        period_start, period_end = self._get_period_boundaries(budget)

        # Get usage in current period
        current_spend = await self.storage.get_user_usage_in_period(user_id, period_start, period_end)

        # Determine limit to use (daily takes precedence if set)
        limit = budget.daily_limit if budget.daily_limit is not None else budget.monthly_limit

        if limit is None:
            # No limit set - allow all requests
            return BudgetCheckResult(
                allowed=True,
                current_spend=current_spend,
                limit=float("inf"),
                percentage_used=0.0,
                remaining_budget=float("inf"),
                should_block=False,
                period_start=period_start,
                period_end=period_end,
                warning=False,
            )

        # Calculate metrics
        percentage_used = (current_spend / limit * 100) if limit > 0 else 0
        remaining_budget = max(0, limit - current_spend)
        should_block = budget.blocking_enabled and current_spend >= limit
        warning = current_spend >= (limit * budget.warning_threshold)

        return BudgetCheckResult(
            allowed=not should_block,
            current_spend=current_spend,
            limit=limit,
            percentage_used=percentage_used,
            remaining_budget=remaining_budget,
            should_block=should_block,
            period_start=period_start,
            period_end=period_end,
            warning=warning and not should_block,
        )

    async def get_budget_status(self, user_id: str) -> dict[str, Any]:
        """Get detailed budget status for a user."""
        result = await self.check_budget(user_id)
        budget = await self.storage.get_budget(user_id)

        return {
            "user_id": user_id,
            "budget_configured": budget is not None,
            "limit": result.limit if result.limit != float("inf") else None,
            "current_spend": result.current_spend,
            "percentage_used": result.percentage_used,
            "remaining_budget": result.remaining_budget if result.remaining_budget != float("inf") else None,
            "period_start": result.period_start.isoformat(),
            "period_end": result.period_end.isoformat(),
            "blocking_enabled": budget.blocking_enabled if budget else False,
        }

    def _get_period_boundaries(self, budget: Budget) -> tuple[datetime, datetime]:
        """Calculate the start and end of the current period."""
        now = self._get_now()

        # Use daily if daily_limit is set, otherwise monthly
        use_daily = budget.daily_limit is not None

        if use_daily:
            # Current day boundaries
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            # Monthly boundaries
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Last day of month
            if now.month == 12:
                period_end = now.replace(
                    year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0
                ) - timedelta(seconds=1)
            else:
                period_end = now.replace(
                    month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0
                ) - timedelta(seconds=1)

        return period_start, period_end
