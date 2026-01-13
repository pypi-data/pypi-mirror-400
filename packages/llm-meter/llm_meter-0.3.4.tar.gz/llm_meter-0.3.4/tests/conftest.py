import pytest
import pytest_asyncio

from llm_meter.context import clear_context
from llm_meter.storage import StorageManager


@pytest_asyncio.fixture
async def storage():
    # Use an in-memory SQLite for tests
    sm = StorageManager("sqlite+aiosqlite:///:memory:")
    await sm.initialize()
    yield sm
    await sm.close()


@pytest.fixture(autouse=True)
def cleanup_context():
    yield
    clear_context()
