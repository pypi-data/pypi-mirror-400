from collections.abc import Awaitable, Callable
from typing import Any, Protocol, runtime_checkable

from llm_meter.models import LLMUsage


@runtime_checkable
class ProviderInstrumenter(Protocol):
    """
    Protocol for provider-specific instrumentation logic.
    """

    def instrument(self, client: Any, storage_callback: Callable[[LLMUsage], Awaitable[Any]]) -> Any:
        """
        Wraps/Instruments the given client to track usage.
        """
        ...


class ProviderRegistry:
    """
    Registry for LLM provider instrumenters to support Open/Closed Principle.
    """

    def __init__(self) -> None:
        self._instrumenters: dict[str, ProviderInstrumenter] = {}

    def register(self, name: str, instrumenter: ProviderInstrumenter) -> None:
        self._instrumenters[name.lower()] = instrumenter

    def get(self, name: str) -> ProviderInstrumenter | None:
        return self._instrumenters.get(name.lower())

    def list_providers(self) -> list[str]:
        return list(self._instrumenters.keys())


# Global registry instance
registry = ProviderRegistry()
