import functools
import inspect
import logging
import time
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable

try:
    import tiktoken  # type: ignore
except ImportError:
    tiktoken = None  # type: ignore

if TYPE_CHECKING:
    from openai import AsyncStream
    from openai.types import CompletionUsage
    from openai.types.chat import ChatCompletion, ChatCompletionChunk

from llm_meter.context import AttributionContext, get_current_context
from llm_meter.models import LLMUsage
from llm_meter.providers.base import ProviderInstrumenter, registry
from llm_meter.providers.pricing import calculate_cost

logger = logging.getLogger(__name__)


@runtime_checkable
class OpenAIUsage(Protocol):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@runtime_checkable
class OpenAIResponse(Protocol):
    model: str
    usage: "CompletionUsage | OpenAIUsage"


F = TypeVar("F", bound=Callable[..., Any])
AF = TypeVar("AF", bound=Callable[..., Awaitable[OpenAIResponse]])


def count_tokens(text: str, model: str) -> int:
    """Fallback token counter using tiktoken."""
    if tiktoken is None:
        logger.warning("tiktoken not installed. Install with 'pip install llm-meter[streaming]' for stream fallbacks.")
        return 0

    try:
        try:
            encoding = tiktoken.encoding_for_model(model)  # type: ignore
        except (KeyError, ValueError):
            encoding = tiktoken.get_encoding("cl100k_base")  # type: ignore
        return len(encoding.encode(text))  # type: ignore
    except Exception as e:
        logger.debug(f"Error counting tokens with tiktoken: {e}")
        return 0


class InstrumentedAsyncStream:
    """Wrapper for OpenAI AsyncStream to capture usage metadata."""

    def __init__(
        self,
        stream: "AsyncStream[ChatCompletionChunk]",
        callback: Callable[[LLMUsage], Awaitable[Any]],
        model: str,
        ctx: AttributionContext,
        start_time: float,
        messages: list[dict[str, Any]] | None = None,
    ):
        self._stream = stream
        self._callback = callback
        self._model = model
        self._ctx = ctx
        self._start_time = start_time
        self._messages = messages or []
        self._usage: CompletionUsage | OpenAIUsage | None = None
        self._content: list[str] = []

    async def __aiter__(self):
        async for chunk in self._stream:
            # Check for official usage in the chunk (usually the last one)
            if hasattr(chunk, "usage") and chunk.usage is not None:
                self._usage = chunk.usage

            # Collect content for fallback counting
            if hasattr(chunk, "choices") and chunk.choices:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    self._content.append(delta.content)

            yield chunk

        # Stream finished, record usage
        latency = int((time.perf_counter() - self._start_time) * 1000)

        if self._usage:
            input_tokens = getattr(self._usage, "prompt_tokens", 0)
            output_tokens = getattr(self._usage, "completion_tokens", 0)
            total_tokens = getattr(self._usage, "total_tokens", 0)
        else:
            # Fallback estimation
            output_text = "".join(self._content)
            output_tokens = count_tokens(output_text, self._model)
            # For input tokens, we estimate from messages
            input_text = " ".join([m.get("content", "") for m in self._messages if isinstance(m.get("content"), str)])
            input_tokens = count_tokens(input_text, self._model)
            total_tokens = input_tokens + output_tokens

        cost = calculate_cost(self._model, input_tokens, output_tokens)

        record = LLMUsage(
            request_id=self._ctx.request_id,
            endpoint=self._ctx.endpoint,
            user_id=self._ctx.user_id,
            feature=self._ctx.feature,
            job_id=self._ctx.job_id,
            provider="openai",
            model=self._model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_estimate=cost,
            latency_ms=latency,
            status="success",
        )
        await self._callback(record)


def instrument_openai_call(provider: str, storage_callback: Callable[[LLMUsage], Awaitable[Any]]) -> Callable[[AF], AF]:
    """
    Decorator/Wrapper for OpenAI-like chat completion calls.
    Extracts usage metadata and records it via the storage_callback.
    """

    def decorator(func: AF) -> AF:
        # Check if already instrumented without triggering pyright errors on the function object
        if getattr(func, "_is_instrumented", False):
            return func

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            ctx = get_current_context()

            try:
                response = await func(*args, **kwargs)

                if kwargs.get("stream"):
                    return InstrumentedAsyncStream(
                        response,  # type: ignore
                        storage_callback,
                        str(kwargs.get("model", "unknown")),
                        ctx,
                        start_time,
                        messages=kwargs.get("messages"),
                    )

                latency_ms = int((time.perf_counter() - start_time) * 1000)

                # Extract usage from OpenAI Response object
                model = response.model
                usage = response.usage

                input_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
                output_tokens = getattr(usage, "completion_tokens", 0) if usage else 0
                total_tokens = getattr(usage, "total_tokens", 0) if usage else 0

                cost = calculate_cost(model, input_tokens, output_tokens)

                record = LLMUsage(
                    request_id=ctx.request_id,
                    endpoint=ctx.endpoint,
                    user_id=ctx.user_id,
                    feature=ctx.feature,
                    job_id=ctx.job_id,
                    provider=provider,
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    cost_estimate=cost,
                    latency_ms=latency_ms,
                    status="success",
                )

                await storage_callback(record)
                return response

            except Exception as e:
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                record = LLMUsage(
                    request_id=ctx.request_id,
                    endpoint=ctx.endpoint,
                    user_id=ctx.user_id,
                    feature=ctx.feature,
                    job_id=ctx.job_id,
                    provider=provider,
                    model=str(kwargs.get("model", "unknown")),
                    status="error",
                    error_message=str(e),
                    latency_ms=latency_ms,
                )
                await storage_callback(record)
                raise e

        # Use setattr to avoid pyright attribute access error on wrapped function
        setattr(async_wrapper, "_is_instrumented", True)  # noqa: B010
        return async_wrapper  # type: ignore

    return decorator  # type: ignore


class OpenAIWrapper(ProviderInstrumenter):
    """
    Dynamically wraps an OpenAI client to instrument chat completion calls.
    """

    def instrument(self, client: Any, storage_callback: Callable[[LLMUsage], Awaitable[Any]]) -> Any:
        return OpenAIClientInstrumenter(client, storage_callback).client


class OpenAIClientInstrumenter:
    """
    Handles the actual patching of the OpenAI client.
    """

    def __init__(self, client: Any, storage_callback: Callable[[LLMUsage], Awaitable[Any]]):
        self.client: Any = client
        self._callback: Callable[[LLMUsage], Awaitable[Any]] = storage_callback
        self._instrument_client()

    def _instrument_client(self) -> None:
        # We target client.chat.completions.create
        if hasattr(self.client, "chat") and hasattr(self.client.chat, "completions"):
            original_create = self.client.chat.completions.create

            if inspect.iscoroutinefunction(original_create):
                self.client.chat.completions.create = self._wrap_async(original_create)
            else:
                self.client.chat.completions.create = self._wrap_sync(original_create)

    def _wrap_async(self, func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            ctx = get_current_context()
            try:
                response = await func(*args, **kwargs)

                if kwargs.get("stream"):
                    return InstrumentedAsyncStream(
                        response,
                        self._callback,
                        str(kwargs.get("model", "unknown")),
                        ctx,
                        start_time,
                        messages=kwargs.get("messages"),
                    )

                await self._record_success(response, start_time, ctx)
                return response
            except Exception as e:
                await self._record_error(e, str(kwargs.get("model", "unknown")), start_time, ctx)
                raise

        return wrapper

    def _wrap_sync(
        self, func: Callable[..., "ChatCompletion | OpenAIResponse"]
    ) -> Callable[..., "ChatCompletion | OpenAIResponse"]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> "ChatCompletion | OpenAIResponse":
            # Note: storage callback must be sync-compatible or run in background
            # For simplicity in v1, we focus on the core wrapping logic.
            return func(*args, **kwargs)

        return wrapper

    async def _record_success(
        self, response: "ChatCompletion | OpenAIResponse", start_time: float, ctx: AttributionContext
    ) -> None:
        latency = int((time.perf_counter() - start_time) * 1000)
        u = response.usage

        input_tokens = getattr(u, "prompt_tokens", 0) if u else 0
        output_tokens = getattr(u, "completion_tokens", 0) if u else 0
        total_tokens = getattr(u, "total_tokens", 0) if u else 0

        cost = calculate_cost(response.model, input_tokens, output_tokens)

        record = LLMUsage(
            request_id=ctx.request_id,
            endpoint=ctx.endpoint,
            user_id=ctx.user_id,
            feature=ctx.feature,
            job_id=ctx.job_id,
            provider="openai",
            model=response.model,
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
            provider="openai",
            model=model,
            status="error",
            error_message=str(e),
            latency_ms=latency,
        )
        await self._callback(record)


# Register the instrumenter
registry.register("openai", OpenAIWrapper())
