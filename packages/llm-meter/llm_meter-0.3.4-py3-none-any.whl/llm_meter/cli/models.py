from datetime import datetime

from pydantic import BaseModel


class UsageExport(BaseModel):
    """Schema for exporting LLM usage data."""

    request_id: str
    endpoint: str | None
    user_id: str | None
    model: str
    provider: str
    total_tokens: int
    cost_estimate: float
    latency_ms: int
    timestamp: datetime
