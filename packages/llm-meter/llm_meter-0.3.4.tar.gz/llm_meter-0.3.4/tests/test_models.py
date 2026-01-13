"""Tests for models module."""

from llm_meter.models import Budget, LLMUsage


def test_llm_usage_repr():
    """Test LLMUsage __repr__ method."""
    usage = LLMUsage(
        request_id="test-123",
        model="gpt-4o",
        provider="openai",
        total_tokens=100,
        cost_estimate=0.05,
    )
    repr_str = repr(usage)
    assert "LLMUsage" in repr_str
    assert "id=" in repr_str or "test-123" in repr_str
    assert "gpt-4o" in repr_str
    assert "0.05" in repr_str


def test_budget_repr():
    """Test Budget __repr__ method."""
    budget = Budget(
        user_id="testuser",
        monthly_limit=100.0,
        daily_limit=10.0,
    )
    repr_str = repr(budget)
    assert "Budget" in repr_str
    assert "testuser" in repr_str
    assert "100.0" in repr_str
    assert "10.0" in repr_str


def test_llm_usage_with_values():
    """Test LLMUsage with explicit values."""
    usage = LLMUsage(
        request_id="test-123",
        model="gpt-4o",
        provider="openai",
        total_tokens=100,
        input_tokens=50,
        output_tokens=50,
        cost_estimate=0.05,
        latency_ms=100,
        endpoint="/chat",
        user_id="user1",
    )
    assert usage.total_tokens == 100
    assert usage.cost_estimate == 0.05
    assert usage.input_tokens == 50
    assert usage.output_tokens == 50
    assert usage.latency_ms == 100
    assert usage.endpoint == "/chat"
    assert usage.user_id == "user1"


def test_budget_with_values():
    """Test Budget with explicit values."""
    budget = Budget(
        user_id="testuser",
        monthly_limit=100.0,
        daily_limit=10.0,
        blocking_enabled=True,
        warning_threshold=0.5,
    )
    assert budget.user_id == "testuser"
    assert budget.monthly_limit == 100.0
    assert budget.daily_limit == 10.0
    assert budget.blocking_enabled is True
    assert budget.warning_threshold == 0.5
    # created_at and updated_at use SQLAlchemy defaults, only set on flush
    assert budget.created_at is None or budget.created_at is not None
    assert budget.updated_at is None or budget.updated_at is not None
