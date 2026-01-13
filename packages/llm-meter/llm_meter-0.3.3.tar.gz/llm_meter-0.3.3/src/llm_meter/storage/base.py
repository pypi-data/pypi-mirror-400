from collections.abc import Sequence
from typing import Any, Protocol, runtime_checkable

from llm_meter.models import LLMUsage


@runtime_checkable
class StorageEngine(Protocol):
    """
    Protocol for storage engines that persist LLM usage data.
    """

    async def initialize(self) -> None:
        """Initialize storage (e.g., create tables)."""
        ...

    async def record_usage(self, usage: LLMUsage) -> None:
        """Persist an LLMUsage record."""
        ...

    async def get_usage_summary(self) -> list[dict[str, Any]]:
        """Retrieve a high-level summary of usage."""
        ...

    async def get_usage_by_endpoint(self) -> list[dict[str, Any]]:
        """Retrieve usage aggregated by endpoint."""
        ...

    async def get_all_usage(self) -> list[LLMUsage]:
        """Retrieve all raw usage records."""
        ...

    async def close(self) -> None:
        """Dispose of resources and close connections."""
        ...

    async def flush(self) -> None:
        """Flush any pending buffered records (optional)."""
        ...

    async def record_batch(self, batch: Sequence[LLMUsage]):
        """
        Optionally implemented by subclasses for batch recording.
        Default: calls record_usage for each item.
        """
        for usage in batch:
            await self.record_usage(usage)
