import logging
from collections.abc import Sequence
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from llm_meter.models import Base, LLMUsage
from llm_meter.storage.base import StorageEngine
from llm_meter.storage.postgres import PostgresStorageManager

logger = logging.getLogger(__name__)


class StorageManager(StorageEngine):
    """
    Handles asynchronous database operations for recording and retrieving LLM usage.
    Default implementation for SQLite.
    """

    def __init__(self, storage_url: str):
        self.storage_url = storage_url
        self.engine = create_async_engine(storage_url, echo=False)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def initialize(self):
        """Create tables if they don't exist."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def record_usage(self, usage: LLMUsage):
        """Persist an LLMUsage record to the database."""
        async with self.session_factory() as session:
            async with session.begin():
                session.add(usage)
            await session.commit()

    async def record_batch(self, batch: Sequence[LLMUsage]):
        """Persist a batch of LLMUsage records to the database in a single transaction."""
        if not batch:
            return
        async with self.session_factory() as session:
            async with session.begin():
                session.add_all(batch)
            await session.commit()

    async def get_usage_summary(self) -> list[dict[str, Any]]:
        """Retrieve a high-level summary of usage."""
        async with self.session_factory() as session:
            stmt = select(
                LLMUsage.model,
                func.sum(LLMUsage.total_tokens).label("total_tokens"),
                func.sum(LLMUsage.cost_estimate).label("total_cost"),
                func.count(LLMUsage.id).label("call_count"),
            ).group_by(LLMUsage.model)

            result = await session.execute(stmt)
            return [dict(row) for row in result.mappings().all()]

    async def get_usage_by_endpoint(self) -> list[dict[str, Any]]:
        """Retrieve usage aggregated by endpoint."""
        async with self.session_factory() as session:
            stmt = select(
                LLMUsage.endpoint,
                func.sum(LLMUsage.total_tokens).label("total_tokens"),
                func.sum(LLMUsage.cost_estimate).label("total_cost"),
            ).group_by(LLMUsage.endpoint)

            result = await session.execute(stmt)
            return [dict(row) for row in result.mappings().all()]

    async def get_all_usage(self) -> list[LLMUsage]:
        """Retrieve all raw usage records."""
        async with self.session_factory() as session:
            result = await session.execute(select(LLMUsage))
            return list(result.scalars().all())

    async def flush(self) -> None:
        """No-op flush for StorageManager (no batching)."""
        return None

    async def close(self):
        """Dispose of the engine."""
        await self.engine.dispose()


def get_storage(url: str) -> StorageEngine:
    """Factory function to get a storage engine instance based on URL scheme."""
    if url.startswith("postgres://") or url.startswith("postgresql://"):
        return PostgresStorageManager(dsn=url)
    # Default to SQLite
    return StorageManager(storage_url=url)
