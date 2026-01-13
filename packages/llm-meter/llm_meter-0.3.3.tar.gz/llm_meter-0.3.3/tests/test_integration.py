import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from llm_meter import FastAPIMiddleware, LLMMeter, get_current_context


@pytest.mark.asyncio
async def test_middleware_context_propagation():
    # Initialize meter with in-memory storage
    meter = LLMMeter(storage_url="sqlite+aiosqlite:///:memory:")
    await meter.initialize()

    app = FastAPI()
    app.add_middleware(FastAPIMiddleware, meter=meter)

    request_id_captured = None

    @app.get("/test")
    async def test_route():
        nonlocal request_id_captured
        ctx = get_current_context()
        request_id_captured = ctx.request_id
        return {"status": "ok", "endpoint": ctx.endpoint}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/test", headers={"X-Request-ID": "custom-id-123"})

    assert response.status_code == 200
    assert response.json()["endpoint"] == "/test"
    assert request_id_captured == "custom-id-123"
    assert response.headers["X-Request-ID"] == "custom-id-123"

    await meter.shutdown()


@pytest.mark.asyncio
async def test_middleware_route_path_capture():
    # Initialize meter
    meter = LLMMeter(storage_url="sqlite+aiosqlite:///:memory:")
    await meter.initialize()

    app = FastAPI()
    app.add_middleware(FastAPIMiddleware, meter=meter)

    captured_endpoint = None

    @app.get("/users/{user_id}")
    async def get_user(user_id: int):
        nonlocal captured_endpoint
        ctx = get_current_context()
        captured_endpoint = ctx.endpoint
        return {"user_id": user_id}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.get("/users/123")

    # It should capture the route template or the path
    assert captured_endpoint in ["/users/{user_id}", "/users/123"]

    await meter.shutdown()
