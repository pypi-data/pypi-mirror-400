from llm_meter.models import LLMUsage
from llm_meter.storage.base import StorageEngine


class DummyStorage(StorageEngine):
    def __init__(self):
        self.recorded = []

    async def initialize(self):
        pass

    async def record_usage(self, usage: LLMUsage):
        self.recorded.append(usage)

    async def get_usage_summary(self):
        return []

    async def get_usage_by_endpoint(self):
        return []

    async def get_all_usage(self):
        return self.recorded

    async def close(self):
        pass

    async def flush(self):
        pass


async def test_record_batch_calls_record_usage():
    dummy = DummyStorage()
    batch = [
        LLMUsage(request_id=str(i), model="m", provider="p", total_tokens=i, cost_estimate=0.1 * i) for i in range(3)
    ]
    await dummy.record_batch(batch)
    assert dummy.recorded == batch
