import logging
from collections.abc import Sequence
from typing import Any

try:
    import asyncpg
except ImportError:
    asyncpg = None  # type: ignore[assignment]

from llm_meter.models import LLMUsage
from llm_meter.storage.base import StorageEngine

logger = logging.getLogger(__name__)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS llm_usage (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(100),
    endpoint VARCHAR(255),
    user_id VARCHAR(100),
    feature VARCHAR(100),
    job_id VARCHAR(100),
    provider VARCHAR(50),
    model VARCHAR(100),
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost_estimate FLOAT DEFAULT 0.0,
    latency_ms INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    timestamp TIMESTAMPTZ DEFAULT (now() at time zone 'utc')
);
"""


class PostgresStorageManager(StorageEngine):
    """
    Storage engine for persisting LLM usage data to a PostgreSQL database.
    Accepts either a DSN string or a pre-configured asyncpg.Pool.
    """

    def __init__(self, dsn: str | None = None, pool: "asyncpg.Pool | None" = None):  # pyright: ignore[reportInvalidTypeForm]
        if asyncpg is None:
            raise ImportError(
                "PostgreSQL support requires 'asyncpg'. Install it with 'pip install llm-meter[postgres]'."
            ) from None
        if not dsn and not pool:
            raise ValueError("Either 'dsn' or 'pool' must be provided to PostgresStorageManager.")

        self.dsn = dsn
        self._pool: asyncpg.Pool | None = pool  # pyright: ignore[reportInvalidTypeForm]
        self._owns_pool = pool is None

    async def initialize(self) -> None:
        """Create a connection pool (if not provided) and ensure the table exists."""
        if self._pool and not self._owns_pool:
            # If pool was provided, just ensure the table exists.
            async with self._pool.acquire() as conn:
                await conn.execute(CREATE_TABLE_SQL)
            logger.info("PostgresStorageManager initialized with existing pool.")
            return

        if self._pool:
            return

        try:
            self._pool = await asyncpg.create_pool(dsn=self.dsn)
            if self._pool:
                async with self._pool.acquire() as conn:
                    await conn.execute(CREATE_TABLE_SQL)
                logger.info("PostgresStorageManager initialized and table verified.")
        except Exception as e:
            logger.error(f"Failed to initialize PostgresStorageManager: {e}")
            raise

    async def record_usage(self, usage: LLMUsage) -> None:
        """Records a single usage record."""
        await self.record_batch([usage])

    async def record_batch(self, batch: Sequence[LLMUsage]) -> None:
        """Efficiently records a batch of usage records."""
        if not self._pool or not batch:
            return

        records_to_insert = [
            (
                u.request_id,
                u.endpoint,
                u.user_id,
                u.feature,
                u.job_id,
                u.provider,
                u.model,
                u.input_tokens,
                u.output_tokens,
                u.total_tokens,
                u.cost_estimate,
                u.latency_ms,
                u.status,
                u.error_message,
                u.timestamp,
            )
            for u in batch
        ]

        try:
            async with self._pool.acquire() as conn:
                await conn.executemany(
                    """
                    INSERT INTO llm_usage (
                        request_id, endpoint, user_id, feature, job_id, provider, model,
                        input_tokens, output_tokens, total_tokens, cost_estimate, latency_ms,
                        status, error_message, timestamp
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                    """,
                    records_to_insert,
                )
        except Exception as e:
            logger.error(f"Failed to record batch to PostgreSQL: {e}")

    async def get_all_usage(self) -> list[LLMUsage]:
        """Retrieve all usage records."""
        if not self._pool:
            return []
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM llm_usage ORDER BY timestamp DESC")
            return [LLMUsage(**dict(row)) for row in rows]

    async def get_usage_summary(self) -> list[dict[str, Any]]:
        """Retrieve usage aggregated by provider and model."""
        if not self._pool:
            return []
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    provider,
                    model,
                    COUNT(*) as call_count,
                    SUM(input_tokens) as total_input_tokens,
                    SUM(output_tokens) as total_output_tokens,
                    SUM(total_tokens) as total_tokens,
                    AVG(latency_ms) as avg_latency_ms,
                    SUM(cost_estimate) as total_cost
                FROM llm_usage
                GROUP BY provider, model
                ORDER BY total_cost DESC
                """
            )
            return [dict(row) for row in rows]

    async def get_usage_by_endpoint(self) -> list[dict[str, Any]]:
        """Retrieve usage aggregated by endpoint."""
        if not self._pool:
            return []
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    endpoint,
                    COUNT(*) as call_count,
                    SUM(total_tokens) as total_tokens,
                    SUM(cost_estimate) as total_cost
                FROM llm_usage
                WHERE endpoint IS NOT NULL
                GROUP BY endpoint
                ORDER BY endpoint
                """
            )
            return [dict(row) for row in rows]

    async def flush(self) -> None:
        """Postgres manager writes immediately, so flush is a no-op."""
        pass

    async def close(self) -> None:
        """Gracefully close the connection pool if we own it."""
        if self._pool and self._owns_pool:
            await self._pool.close()
            self._pool = None
            logger.info("PostgresStorageManager connection pool closed.")
