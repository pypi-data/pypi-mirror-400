import functools
import inspect
import logging
import time
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    # Use Any for SDK types to avoid hard dependency at runtime
    pass

from llm_meter.context import AttributionContext, get_current_context
from llm_meter.models import LLMUsage
from llm_meter.providers.base import ProviderInstrumenter, registry
from llm_meter.providers.pricing import calculate_cost

logger = logging.getLogger(__name__)

# Pattern for Anthropic is similar to OpenAI but with different field names and stream handling.


@runtime_checkable
class AnthropicUsage(Protocol):
    input_tokens: int
    output_tokens: int


@runtime_checkable
class AnthropicMessage(Protocol):
    model: str
    usage: AnthropicUsage


class InstrumentedAnthropicStream:
    """Wrapper for Anthropic stream to capture usage metadata."""

    def __init__(
        self,
        stream: Any,
        callback: Callable[[LLMUsage], Awaitable[Any]],
        model: str,
        ctx: AttributionContext,
        start_time: float,
    ):
        self._stream = stream
        self._callback = callback
        self._model = model
        self._ctx = ctx
        self._start_time = start_time
        self._input_tokens = 0
        self._output_tokens = 0

    async def __aiter__(self):
        async for event in self._stream:
            # Anthropic streaming events structure:
            # message_start -> contains input_tokens
            # message_delta -> contains accumulated output_tokens

            event_type = getattr(event, "type", None)

            if event_type == "message_start":
                msg = getattr(event, "message", None)
                usage = getattr(msg, "usage", None)
                if usage:
                    self._input_tokens = getattr(usage, "input_tokens", 0)

            elif event_type == "message_delta":
                usage = getattr(event, "usage", None)
                if usage:
                    self._output_tokens = getattr(usage, "output_tokens", 0)

            yield event

        # Stream finished, record usage
        latency = int((time.perf_counter() - self._start_time) * 1000)
        total_tokens = self._input_tokens + self._output_tokens
        cost = calculate_cost(self._model, self._input_tokens, self._output_tokens)

        record = LLMUsage(
            request_id=self._ctx.request_id,
            endpoint=self._ctx.endpoint,
            user_id=self._ctx.user_id,
            feature=self._ctx.feature,
            job_id=self._ctx.job_id,
            provider="anthropic",
            model=self._model,
            input_tokens=self._input_tokens,
            output_tokens=self._output_tokens,
            total_tokens=total_tokens,
            cost_estimate=cost,
            latency_ms=latency,
            status="success",
        )
        await self._callback(record)


class AnthropicWrapper(ProviderInstrumenter):
    """
    Dynamically wraps an Anthropic client to instrument message creation.
    """

    def instrument(self, client: Any, storage_callback: Callable[[LLMUsage], Awaitable[Any]]) -> Any:
        return AnthropicClientInstrumenter(client, storage_callback).client


class AnthropicClientInstrumenter:
    """
    Handles the actual patching of the Anthropic client.
    """

    def __init__(self, client: Any, storage_callback: Callable[[LLMUsage], Awaitable[Any]]):
        self.client: Any = client
        self._callback: Callable[[LLMUsage], Awaitable[Any]] = storage_callback
        self._instrument_client()

    def _instrument_client(self) -> None:
        # Anthropic SDK: client.messages.create
        if hasattr(self.client, "messages"):
            original_create = self.client.messages.create

            if inspect.iscoroutinefunction(original_create):
                self.client.messages.create = self._wrap_async(original_create)
            else:
                self.client.messages.create = self._wrap_sync(original_create)

    def _wrap_async(self, func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            ctx = get_current_context()
            try:
                response = await func(*args, **kwargs)

                if kwargs.get("stream"):
                    return InstrumentedAnthropicStream(
                        response,
                        self._callback,
                        str(kwargs.get("model", "unknown")),
                        ctx,
                        start_time,
                    )

                await self._record_success(response, start_time, ctx)
                return response
            except Exception as e:
                await self._record_error(e, str(kwargs.get("model", "unknown")), start_time, ctx)
                raise

        return wrapper

    def _wrap_sync(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Sync support - simple pass-through for now or implement if needed
            # Anthropic also has a sync client.
            return func(*args, **kwargs)

        return wrapper

    async def _record_success(self, response: Any, start_time: float, ctx: AttributionContext) -> None:
        latency = int((time.perf_counter() - start_time) * 1000)

        # response should have model and usage attributes
        model = getattr(response, "model", "unknown")
        usage = getattr(response, "usage", None)

        input_tokens = getattr(usage, "input_tokens", 0) if usage else 0
        output_tokens = getattr(usage, "output_tokens", 0) if usage else 0
        total_tokens = input_tokens + output_tokens

        cost = calculate_cost(model, input_tokens, output_tokens)

        record = LLMUsage(
            request_id=ctx.request_id,
            endpoint=ctx.endpoint,
            user_id=ctx.user_id,
            feature=ctx.feature,
            job_id=ctx.job_id,
            provider="anthropic",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_estimate=cost,
            latency_ms=latency,
            status="success",
        )
        await self._callback(record)

    async def _record_error(self, e: Exception, model: str, start_time: float, ctx: AttributionContext) -> None:
        latency = int((time.perf_counter() - start_time) * 1000)
        record = LLMUsage(
            request_id=ctx.request_id,
            endpoint=ctx.endpoint,
            user_id=ctx.user_id,
            feature=ctx.feature,
            job_id=ctx.job_id,
            provider="anthropic",
            model=model,
            status="error",
            error_message=str(e),
            latency_ms=latency,
        )
        await self._callback(record)


# Register the instrumenter
registry.register("anthropic", AnthropicWrapper())
