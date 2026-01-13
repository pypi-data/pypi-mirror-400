import contextvars
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AttributionContext(BaseModel):
    """
    Holds metadata for LLM cost attribution.
    Pydantic allows for easy validation and FastAPI integration.
    """

    request_id: str = Field(default_factory=lambda: str(uuid4()))
    endpoint: str | None = None
    user_id: str | None = None
    feature: str | None = None
    job_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert context to a dictionary for storage or logging."""
        return self.model_dump()


# Internal context storage using contextvars for async-safety
_current_context: contextvars.ContextVar[AttributionContext | None] = contextvars.ContextVar(
    "llm_meter_context", default=None
)


def get_current_context() -> AttributionContext:
    """
    Retrieve the current attribution context.
    If no context exists, a default one with a new request_id is returned.
    """
    ctx = _current_context.get()
    if ctx is None:
        ctx = AttributionContext()
        _current_context.set(ctx)
    return ctx


def set_current_context(ctx: AttributionContext) -> contextvars.Token[AttributionContext | None]:
    """
    Set the current attribution context.
    Returns a token that can be used to reset the context later.
    """
    return _current_context.set(ctx)


def update_current_context(**kwargs: Any) -> contextvars.Token[AttributionContext | None]:
    """
    Update the current context with new values.
    This creates a new AttributionContext object and sets it using Pydantic's model_copy.
    """
    current = get_current_context()
    new_ctx = current.model_copy(update=kwargs)
    return set_current_context(new_ctx)


def clear_context(token: contextvars.Token[AttributionContext | None] | None = None) -> None:
    """
    Reset the context. If a token is provided, it resets to the previous state.
    Otherwise, it sets the context to None.
    """
    if token:
        _current_context.reset(token)
    else:
        _current_context.set(None)


@contextmanager
def attribution_context(**kwargs: Any) -> Generator[AttributionContext, None, None]:
    """
    Context manager for setting attribution context for a block of code.
    """
    token = update_current_context(**kwargs)
    try:
        yield get_current_context()
    finally:
        clear_context(token)
