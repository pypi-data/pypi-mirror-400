import logging
from collections.abc import Sequence
from datetime import datetime
from typing import Any

try:
    import asyncpg  # pyright: ignore[reportMissingTypeStubs]
except ImportError:
    asyncpg = None  # type: ignore[assignment]

from llm_meter.models import Budget, LLMUsage
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

CREATE_BUDGETS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS budgets (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    monthly_limit FLOAT,
    daily_limit FLOAT,
    blocking_enabled BOOLEAN DEFAULT FALSE,
    warning_threshold FLOAT DEFAULT 0.8,
    created_at TIMESTAMPTZ DEFAULT (now() at time zone 'utc'),
    updated_at TIMESTAMPTZ DEFAULT (now() at time zone 'utc')
);
"""


class PostgresStorageManager(StorageEngine):
    """
    Storage engine for persisting LLM usage data to a PostgreSQL database.
    Accepts either a DSN string or a pre-configured asyncpg.Pool.
    """

    def __init__(self, dsn: str | None = None, pool: "asyncpg.Pool | None" = None):  # type: ignore
        if asyncpg is None:
            raise ImportError(
                "PostgreSQL support requires 'asyncpg'. Install it with 'pip install llm-meter[postgres]'."
            ) from None
        if not dsn and not pool:
            raise ValueError("Either 'dsn' or 'pool' must be provided to PostgresStorageManager.")

        self.dsn = dsn
        self._pool: asyncpg.Pool | None = pool  # type: ignore
        self._owns_pool = pool is None

    async def _ensure_tables_exist(self) -> None:
        """Execute table creation SQL statements."""
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            await conn.execute(CREATE_TABLE_SQL)
            await conn.execute(CREATE_BUDGETS_TABLE_SQL)

    async def initialize(self) -> None:
        """Create a connection pool (if not provided) and ensure the table exists."""
        if not self._owns_pool:
            # External pool provided - just ensure tables exist
            await self._ensure_tables_exist()
            logger.info("PostgresStorageManager initialized with existing pool.")
            return

        if self._pool:
            # Already initialized with our own pool - no-op
            return

        # Create our own pool and ensure tables exist
        try:
            self._pool = await asyncpg.create_pool(dsn=self.dsn)
            await self._ensure_tables_exist()
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

    # Budget-related methods

    async def get_user_usage_in_period(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        """Get total cost for a user in a time period."""
        if not self._pool:
            return 0.0
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT COALESCE(SUM(cost_estimate), 0.0) as total_cost
                FROM llm_usage
                WHERE user_id = $1 AND timestamp >= $2 AND timestamp <= $3
                """,
                user_id,
                start_date,
                end_date,
            )
            return float(row["total_cost"]) if row else 0.0

    async def get_budget(self, user_id: str) -> Budget | None:
        """Get budget configuration for a user."""
        if not self._pool:
            return None
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, user_id, monthly_limit, daily_limit, blocking_enabled,
                       warning_threshold, created_at, updated_at
                FROM budgets
                WHERE user_id = $1
                """,
                user_id,
            )
            if row:
                return Budget(
                    id=row["id"],
                    user_id=row["user_id"],
                    monthly_limit=row["monthly_limit"],
                    daily_limit=row["daily_limit"],
                    blocking_enabled=row["blocking_enabled"],
                    warning_threshold=row["warning_threshold"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            return None

    async def upsert_budget(self, budget: Budget) -> None:
        """Create or update a budget."""
        if not self._pool:
            return
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO budgets (user_id, monthly_limit, daily_limit, blocking_enabled, warning_threshold)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (user_id) DO UPDATE SET
                    monthly_limit = EXCLUDED.monthly_limit,
                    daily_limit = EXCLUDED.daily_limit,
                    blocking_enabled = EXCLUDED.blocking_enabled,
                    warning_threshold = EXCLUDED.warning_threshold,
                    updated_at = now()
                """,
                budget.user_id,
                budget.monthly_limit,
                budget.daily_limit,
                budget.blocking_enabled,
                budget.warning_threshold,
            )

    async def delete_budget(self, user_id: str) -> None:
        """Delete a user's budget."""
        if not self._pool:
            return
        async with self._pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM budgets WHERE user_id = $1",
                user_id,
            )

    async def get_all_budgets(self) -> list[Budget]:
        """Get all budget configurations."""
        if not self._pool:
            return []
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, user_id, monthly_limit, daily_limit, blocking_enabled,
                       warning_threshold, created_at, updated_at
                FROM budgets
                ORDER BY user_id
                """
            )
            return [
                Budget(
                    id=row["id"],
                    user_id=row["user_id"],
                    monthly_limit=row["monthly_limit"],
                    daily_limit=row["daily_limit"],
                    blocking_enabled=row["blocking_enabled"],
                    warning_threshold=row["warning_threshold"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                for row in rows
            ]
