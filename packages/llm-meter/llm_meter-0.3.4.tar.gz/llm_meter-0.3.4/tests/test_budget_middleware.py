"""Tests for budget middleware functionality."""

from datetime import datetime, timezone

import pytest
from starlette.requests import Request
from starlette.responses import Response

from llm_meter.budget import BudgetCheckResult, BudgetManager
from llm_meter.budget_middleware import BudgetMiddleware
from llm_meter.models import Budget


class MockStorage:
    """Mock storage for testing BudgetMiddleware."""

    def __init__(self):
        self.budgets: dict[str, Budget] = {}
        self.usage: list[dict] = []

    async def get_budget(self, user_id: str) -> Budget | None:
        return self.budgets.get(user_id)

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

    async def initialize(self) -> None:
        pass

    async def close(self) -> None:
        pass


def create_mock_app():
    """Create a mock ASGI app for testing."""

    async def app(scope, receive, send):
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": b"OK",
            }
        )

    return app


@pytest.fixture
def mock_storage():
    return MockStorage()


@pytest.fixture
def budget_manager(mock_storage):
    return BudgetManager(mock_storage)


@pytest.fixture
def mock_app():
    return create_mock_app()


def create_budget_result(
    allowed: bool = True,
    current_spend: float = 10.0,
    limit: float = 100.0,
    percentage_used: float = 10.0,
    remaining_budget: float = 90.0,
    should_block: bool = False,
    warning: bool = False,
) -> BudgetCheckResult:
    """Create a BudgetCheckResult for testing."""
    now = datetime.now(timezone.utc)
    return BudgetCheckResult(
        allowed=allowed,
        current_spend=current_spend,
        limit=limit,
        percentage_used=percentage_used,
        remaining_budget=remaining_budget,
        should_block=should_block,
        period_start=now,
        period_end=now,
        warning=warning,
    )


async def test_middleware_excludes_health_path(mock_app, budget_manager):
    """Test that /health path is excluded from budget checking."""
    middleware = BudgetMiddleware(mock_app, budget_manager)

    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/health",
            "headers": [(b"x-user-id", b"user_123")],
        }
    )

    call_next_called = False

    async def call_next(req):
        nonlocal call_next_called
        call_next_called = True
        return Response("OK", status_code=200)

    response = await middleware.dispatch(request, call_next)

    assert call_next_called is True
    assert response.status_code == 200


async def test_middleware_excludes_metrics_path(mock_app, budget_manager):
    """Test that /metrics path is excluded from budget checking."""
    middleware = BudgetMiddleware(mock_app, budget_manager)

    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/metrics",
            "headers": [(b"x-user-id", b"user_123")],
        }
    )

    call_next_called = False

    async def call_next(req):
        nonlocal call_next_called
        call_next_called = True
        return Response("OK", status_code=200)

    response = await middleware.dispatch(request, call_next)

    assert call_next_called is True
    assert response.status_code == 200


async def test_middleware_excludes_docs_path(mock_app, budget_manager):
    """Test that /docs path is excluded from budget checking."""
    middleware = BudgetMiddleware(mock_app, budget_manager)

    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/docs",
            "headers": [(b"x-user-id", b"user_123")],
        }
    )

    call_next_called = False

    async def call_next(req):
        nonlocal call_next_called
        call_next_called = True
        return Response("OK", status_code=200)

    response = await middleware.dispatch(request, call_next)

    assert call_next_called is True
    assert response.status_code == 200


async def test_middleware_excludes_openapi_path(mock_app, budget_manager):
    """Test that /openapi path is excluded from budget checking."""
    middleware = BudgetMiddleware(mock_app, budget_manager)

    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/openapi.json",
            "headers": [(b"x-user-id", b"user_123")],
        }
    )

    call_next_called = False

    async def call_next(req):
        nonlocal call_next_called
        call_next_called = True
        return Response("OK", status_code=200)

    response = await middleware.dispatch(request, call_next)

    assert call_next_called is True
    assert response.status_code == 200


async def test_middleware_skips_when_no_user_header(mock_app, budget_manager):
    """Test that budget check is skipped when X-User-ID header is missing."""
    middleware = BudgetMiddleware(mock_app, budget_manager)

    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/api/endpoint",
            "headers": [],
        }
    )

    call_next_called = False

    async def call_next(req):
        nonlocal call_next_called
        call_next_called = True
        return Response("OK", status_code=200)

    response = await middleware.dispatch(request, call_next)

    assert call_next_called is True
    assert response.status_code == 200


async def test_middleware_blocks_when_budget_exceeded_with_blocking(mock_app, budget_manager, mock_storage):
    """Test that requests are blocked when budget is exceeded and blocking is enabled."""
    # Setup budget with blocking enabled
    budget = Budget(
        user_id="user_123",
        monthly_limit=100.0,
        blocking_enabled=True,
        warning_threshold=0.8,
    )
    mock_storage.budgets["user_123"] = budget
    mock_storage.usage.append(
        {
            "user_id": "user_123",
            "timestamp": datetime.now(timezone.utc),
            "cost": 150.0,  # Exceeds limit
        }
    )

    middleware = BudgetMiddleware(mock_app, budget_manager)

    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/chat",
            "headers": [(b"x-user-id", b"user_123")],
        }
    )

    async def call_next(req):
        return Response("OK", status_code=200)

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 429  # Too Many Requests
    assert "X-Budget-Limit" in response.headers
    assert "X-Budget-Current" in response.headers
    assert "X-Budget-Percentage" in response.headers
    assert response.headers["X-Budget-Limit"] == "100.0000"
    assert response.headers["X-Budget-Current"] == "150.0000"


async def test_middleware_blocking_disabled_allows_request(mock_app, budget_manager, mock_storage):
    """Test that when blocking is disabled, requests are allowed even when over limit."""
    budget = Budget(
        user_id="user_123",
        monthly_limit=100.0,
        blocking_enabled=False,
        warning_threshold=0.8,
    )
    mock_storage.budgets["user_123"] = budget
    mock_storage.usage.append(
        {
            "user_id": "user_123",
            "timestamp": datetime.now(timezone.utc),
            "cost": 150.0,  # Exceeds limit
        }
    )

    middleware = BudgetMiddleware(mock_app, budget_manager)

    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/chat",
            "headers": [(b"x-user-id", b"user_123")],
        }
    )

    async def call_next(req):
        return Response("OK", status_code=200)

    response = await middleware.dispatch(request, call_next)

    # Should be allowed since blocking is disabled
    assert response.status_code == 200


async def test_middleware_adds_headers_to_response_when_budget_configured(mock_app, budget_manager, mock_storage):
    """Test that budget headers are added to successful responses when budget is configured."""
    budget = Budget(
        user_id="user_123",
        monthly_limit=100.0,
        blocking_enabled=True,
        warning_threshold=0.8,
    )
    mock_storage.budgets["user_123"] = budget
    mock_storage.usage.append(
        {
            "user_id": "user_123",
            "timestamp": datetime.now(timezone.utc),
            "cost": 50.0,
        }
    )

    middleware = BudgetMiddleware(mock_app, budget_manager)

    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/chat",
            "headers": [(b"x-user-id", b"user_123")],
        }
    )

    async def call_next(req):
        response = Response("OK", status_code=200)
        return response

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 200
    assert "X-Budget-Limit" in response.headers
    assert "X-Budget-Current" in response.headers
    assert "X-Budget-Percentage" in response.headers
    assert response.headers["X-Budget-Limit"] == "100.0000"
    assert response.headers["X-Budget-Current"] == "50.0000"
    assert response.headers["X-Budget-Percentage"] == "50.0"


async def test_middleware_no_headers_when_no_budget_configured(mock_app, budget_manager):
    """Test that no budget headers are added when no budget is configured."""
    middleware = BudgetMiddleware(mock_app, budget_manager)

    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/chat",
            "headers": [(b"x-user-id", b"user_123")],
        }
    )

    async def call_next(req):
        response = Response("OK", status_code=200)
        return response

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 200
    assert "X-Budget-Limit" not in response.headers


async def test_middleware_custom_paths_to_exclude(mock_app, budget_manager):
    """Test that custom paths to exclude are honored."""
    middleware = BudgetMiddleware(mock_app, budget_manager, paths_to_exclude=["/custom-path", "/admin"])

    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/custom-path",
            "headers": [(b"x-user-id", b"user_123")],
        }
    )

    call_next_called = False

    async def call_next(req):
        nonlocal call_next_called
        call_next_called = True
        return Response("OK", status_code=200)

    _ = await middleware.dispatch(request, call_next)

    assert call_next_called is True


async def test_middleware_custom_header_name(mock_app, budget_manager, mock_storage):
    """Test that custom header name is used to get user ID."""
    budget = Budget(
        user_id="user_123",
        monthly_limit=100.0,
        blocking_enabled=True,
        warning_threshold=0.8,
    )
    mock_storage.budgets["user_123"] = budget
    mock_storage.usage.append(
        {
            "user_id": "user_123",
            "timestamp": datetime.now(timezone.utc),
            "cost": 50.0,
        }
    )

    middleware = BudgetMiddleware(mock_app, budget_manager, header_name="X-Custom-User")

    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/chat",
            "headers": [(b"x-custom-user", b"user_123")],
        }
    )

    async def call_next(req):
        response = Response("OK", status_code=200)
        return response

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 200
    assert "X-Budget-Limit" in response.headers
