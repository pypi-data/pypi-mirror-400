import os
from typing import Any

import uvicorn
from fastapi import FastAPI
from openai import AsyncOpenAI
from pydantic import BaseModel

from llm_meter import FastAPIMiddleware, LLMMeter, update_current_context

# 1. Initialize the LLMMeter SDK
# We use a local SQLite file for this example.
meter = LLMMeter(
    storage_url="sqlite+aiosqlite:///example_usage.db",
)

app = FastAPI(title="llm-meter Example App")

# 2. Add the Middleware
# This automatically tracks endpoints and generates request IDs.
app.add_middleware(FastAPIMiddleware, meter=meter)

# 3. Wrap your LLM Client
# You only need to do this once.
client = meter.wrap_client(AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", "sk-mock-key")))


class ChatRequest(BaseModel):
    prompt: str
    user_id: str | None = None


# 4. Dependency to set extra context (optional)
def set_user_context(user_id: str | None = None) -> None:
    if user_id:
        update_current_context(user_id=user_id)


@app.on_event("startup")
async def startup_event() -> None:
    # Initialize the database tables
    await meter.initialize()


@app.post("/chat")
async def chat(req: ChatRequest) -> dict[str, Any]:
    # Set the user ID in the context if provided
    if req.user_id:
        update_current_context(user_id=req.user_id)

    # This call is automatically instrumented!
    # It will be attributed to the "/chat" endpoint.
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": req.prompt}],
        )
        return {
            "reply": response.choices[0].message.content,
            "usage": response.usage.model_dump() if response.usage else None,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/status")
async def status() -> dict[str, str]:
    return {"status": "llm-meter is active"}


if __name__ == "__main__":
    print("🚀 Starting Example App...")
    print("💡 Run 'uv run llm-meter usage summary' in another terminal to see stats.")
    uvicorn.run(app, host="0.0.0.0", port=8000)
