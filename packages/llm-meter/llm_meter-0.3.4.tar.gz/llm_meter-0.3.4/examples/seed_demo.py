import asyncio
import random

from llm_meter import LLMMeter
from llm_meter.models import LLMUsage


async def seed_data():
    meter = LLMMeter(storage_url="sqlite+aiosqlite:///example_usage.db")
    await meter.initialize()

    models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
    endpoints = ["/chat", "/summarize", "/translate"]

    print("🌱 Seeding 20 mock LLM usage records...")

    for i in range(20):
        model = random.choice(models)
        endpoint = random.choice(endpoints)
        input_tokens = random.randint(100, 1000)
        output_tokens = random.randint(50, 500)

        # Simple cost calculation for seeding
        rate = 0.005 if "mini" not in model else 0.0001
        cost = (input_tokens + output_tokens) / 1000 * rate

        usage = LLMUsage(
            request_id=f"seed-{i}",
            endpoint=endpoint,
            user_id=f"user-{random.randint(1, 5)}",
            provider="openai",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_estimate=cost,
            latency_ms=random.randint(200, 1500),
            status="success",
        )
        await meter.storage.record_usage(usage)

    await meter.shutdown()
    print("✅ Done! You can now run:")
    print("   uv run llm-meter usage summary --storage-url sqlite+aiosqlite:///example_usage.db")


if __name__ == "__main__":
    asyncio.run(seed_data())
