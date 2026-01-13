"""FastAPI middleware for automated budget checking and blocking."""

import logging
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from llm_meter.budget import BudgetManager

logger = logging.getLogger(__name__)


class BudgetMiddleware(BaseHTTPMiddleware):
    """
    Middleware that checks budget limits before allowing requests.
    Can be used alongside FastAPIMiddleware for combined context + budget checking.
    """

    def __init__(
        self,
        app: ASGIApp,
        budget_manager: BudgetManager,
        paths_to_exclude: list[str] | None = None,
        header_name: str = "X-User-ID",
    ) -> None:
        super().__init__(app)
        self.budget_manager = budget_manager
        self.paths_to_exclude = paths_to_exclude or ["/health", "/metrics", "/docs", "/openapi"]
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.paths_to_exclude):
            return await call_next(request)

        # Get user_id from header
        user_id = request.headers.get(self.header_name)

        if not user_id:
            # No user identification - skip budget check
            return await call_next(request)

        # Check budget
        result = await self.budget_manager.check_budget(user_id)

        # Log warning if approaching limit
        if result.warning:
            logger.warning(
                f"User {user_id} is approaching budget limit: "
                f"{result.percentage_used:.1f}% used (${result.current_spend:.4f}/${result.limit:.4f})"
            )

        # Block if over budget
        if not result.allowed:
            logger.warning(
                f"User {user_id} exceeded budget limit: "
                f"{result.percentage_used:.1f}% (${result.current_spend:.4f}/${result.limit:.4f})"
            )

            # Include budget info in response headers
            headers: dict[str, str] = {
                "X-Budget-Limit": f"{result.limit:.4f}",
                "X-Budget-Current": f"{result.current_spend:.4f}",
                "X-Budget-Percentage": f"{result.percentage_used:.1f}",
            }

            return JSONResponse(
                status_code=429 if result.should_block else 402,
                content={
                    "error": "budget_exceeded",
                    "message": (
                        f"Budget limit exceeded. Current spend: ${result.current_spend:.4f}, Limit: ${result.limit:.4f}"
                    ),
                    "current_spend": result.current_spend,
                    "limit": result.limit,
                    "period_start": result.period_start.isoformat(),
                    "period_end": result.period_end.isoformat(),
                },
                headers=headers,
            )

        # Continue with request
        response = await call_next(request)

        # Add budget info headers to response (only if budget is configured)
        if result.limit != float("inf"):
            response.headers["X-Budget-Limit"] = f"{result.limit:.4f}"
            response.headers["X-Budget-Current"] = f"{result.current_spend:.4f}"
            response.headers["X-Budget-Percentage"] = f"{result.percentage_used:.1f}"

        return response
