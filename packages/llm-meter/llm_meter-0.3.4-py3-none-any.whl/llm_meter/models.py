from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base class for all models."""

    pass


class LLMUsage(Base):
    """
    Records usage, cost, and metadata for a single LLM call.
    """

    __tablename__ = "llm_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    request_id: Mapped[str] = mapped_column(String(100), index=True)
    endpoint: Mapped[str | None] = mapped_column(String(255), index=True)
    user_id: Mapped[str | None] = mapped_column(String(100), index=True)
    feature: Mapped[str | None] = mapped_column(String(100), index=True)
    job_id: Mapped[str | None] = mapped_column(String(100), index=True)

    provider: Mapped[str] = mapped_column(String(50), index=True)
    model: Mapped[str] = mapped_column(String(100), index=True)

    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)

    cost_estimate: Mapped[float] = mapped_column(Float, default=0.0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[str] = mapped_column(String(20), default="success")
    error_message: Mapped[str | None] = mapped_column(Text)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    def __repr__(self) -> str:
        return f"<LLMUsage(id={self.id}, model='{self.model}', cost={self.cost_estimate})>"


class Budget(Base):
    """
    Stores budget limits and current consumption for users.
    """

    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # Budget limits
    monthly_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    daily_limit: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Configuration
    blocking_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    warning_threshold: Mapped[float] = mapped_column(Float, default=0.8)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<Budget(user_id='{self.user_id}', monthly_limit={self.monthly_limit}, daily_limit={self.daily_limit})>"
