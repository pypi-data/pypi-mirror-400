import asyncio
import contextlib
import logging
from datetime import datetime
from typing import Any

from llm_meter.models import Budget, LLMUsage
from llm_meter.storage.base import StorageEngine

logger = logging.getLogger(__name__)


class BatchingStorageManager(StorageEngine):
    """
    Wraps another StorageEngine to provide asynchronous batching.
    Uses an internal queue to buffer records and flushes them in chunks.
    """

    def __init__(
        self,
        base_engine: StorageEngine,
        batch_size: int = 10,
        flush_interval: float = 5.0,
    ):
        self.base_engine = base_engine
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._queue: asyncio.Queue[LLMUsage] = asyncio.Queue()
        self._worker_task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()

    async def initialize(self):
        await self.base_engine.initialize()
        # Start background worker
        self._worker_task = asyncio.create_task(self._worker())

    async def record_usage(self, usage: LLMUsage):
        await self._queue.put(usage)
        # If queue is large, we could potentially signal the worker,
        # but the worker is already watching the queue.

    async def _worker(self):
        """Background loop that flushes periodically or when batch size is reached."""
        while not self._stop_event.is_set():
            batch: list[LLMUsage] = []
            try:
                # Wait for the first item
                item = await asyncio.wait_for(self._queue.get(), timeout=self.flush_interval)
                batch.append(item)

                # Pull more items if available, up to batch_size
                while len(batch) < self.batch_size and not self._queue.empty():
                    batch.append(self._queue.get_nowait())

            except asyncio.TimeoutError:
                # No new items for flush_interval, proceed to flush what we have (if anything)
                pass
            except Exception as e:
                logger.error(f"Error in batch worker: {e}")

            if batch:
                await self._flush_batch(batch)
                for _ in range(len(batch)):
                    self._queue.task_done()

    async def _flush_batch(self, batch: list[LLMUsage]):
        """Actually flushes the batch to the base engine."""
        try:
            # We need to extend StorageEngine or StorageManager to support record_batch
            # For now, we call record_usage in a loop within a single transaction if possible
            # But the base StorageManager writes one by one.
            # Let's check if we should add record_batch to the base StorageManager.
            if hasattr(self.base_engine, "record_batch"):
                await self.base_engine.record_batch(batch)
            else:
                for usage in batch:
                    await self.base_engine.record_usage(usage)
        except Exception as e:
            logger.error(f"Failed to flush batch of {len(batch)} records: {e}")

    async def flush(self):
        """Force a flush of all remaining items in the queue."""
        batch: list[LLMUsage] = []
        while not self._queue.empty():
            batch.append(self._queue.get_nowait())
            self._queue.task_done()

        if batch:
            await self._flush_batch(batch)

    async def close(self):
        self._stop_event.set()
        if self._worker_task:
            # Cancel the worker if it's waiting for items
            self._worker_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._worker_task

        # Final flush
        await self.flush()
        await self.base_engine.close()

    # Proxy other methods to base_engine
    async def get_usage_summary(self) -> list[dict[str, Any]]:
        return await self.base_engine.get_usage_summary()

    async def get_usage_by_endpoint(self) -> list[dict[str, Any]]:
        return await self.base_engine.get_usage_by_endpoint()

    async def get_all_usage(self) -> list[LLMUsage]:
        return await self.base_engine.get_all_usage()

    # Budget-related method proxies

    async def get_user_usage_in_period(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        return await self.base_engine.get_user_usage_in_period(user_id, start_date, end_date)

    async def get_budget(self, user_id: str) -> Budget | None:
        return await self.base_engine.get_budget(user_id)

    async def upsert_budget(self, budget: Budget) -> None:
        return await self.base_engine.upsert_budget(budget)

    async def delete_budget(self, user_id: str) -> None:
        return await self.base_engine.delete_budget(user_id)

    async def get_all_budgets(self) -> list[Budget]:
        return await self.base_engine.get_all_budgets()
