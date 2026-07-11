import asyncio
import json
from typing import Iterable

from app.models import AgentResponse


class ChatStreamService:
    def __init__(self, delay: float = 0.5):
        self.delay = delay

    async def generate_stream(self, data: Iterable[AgentResponse]):
        for item in data:
            payload = json.dumps(item.model_dump(mode="json")) + "\n"
            yield payload
            await asyncio.sleep(self.delay)
