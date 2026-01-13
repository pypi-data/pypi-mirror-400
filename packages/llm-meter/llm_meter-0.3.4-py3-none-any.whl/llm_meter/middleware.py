import logging
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from llm_meter.context import AttributionContext, clear_context, set_current_context
from llm_meter.core import LLMMeter

logger = logging.getLogger(__name__)


class FastAPIMiddleware(BaseHTTPMiddleware):
    """
    FastAPI/Starlette middleware that initializes the attribution context
    for each request and captures the endpoint.
    """

    def __init__(self, app: ASGIApp, meter: LLMMeter) -> None:
        super().__init__(app)
        self.meter = meter

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = str(request.headers.get("X-Request-ID", str(uuid.uuid4())))
        user_id = request.headers.get("X-User-ID")
        endpoint = request.url.path
        route = request.scope.get("route")
        if route:  # pragma: no cover
            # Starlette Route objects have a .path attribute
            path_attr = getattr(route, "path", None)
            if path_attr:
                endpoint = str(path_attr)

        ctx = AttributionContext(request_id=request_id, endpoint=endpoint, user_id=user_id)

        token = set_current_context(ctx)

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            clear_context(token)
