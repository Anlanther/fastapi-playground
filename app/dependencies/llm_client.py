"""Placeholder LLM client provider for LangGraph / LM Studio.

This is a minimal factory to be replaced with a real LangGraph client
initialization once the project adds the appropriate dependency.
"""
import asyncio
import json
from typing import Any

import httpx

from app.core.config import settings


class HTTPStreamLLMClient:
    """Simple HTTP streaming client for LangGraph / LM Studio endpoints.

    Expects `settings.langgraph_endpoint` to be a full URL that accepts a
    POST with JSON {"input": "..."} and responds with a streaming
    (chunked) body containing newline-delimited JSON or text chunks.
    """

    def __init__(self, endpoint: str | None, api_key: str | None = None, timeout: float = 60.0):
        self.endpoint = endpoint
        self.api_key = api_key
        self.timeout = timeout

    async def stream(self, prompt: str):
        if not self.endpoint:
            raise RuntimeError(
                "LangGraph endpoint not configured (settings.langgraph_endpoint)")

        headers = {"Accept": "text/event-stream",
                   "Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                async with client.stream("POST", self.endpoint, json={"input": prompt}, headers=headers) as resp:
                    resp.raise_for_status()
                    async for raw_chunk in resp.aiter_lines():
                        if not raw_chunk:
                            continue
                        # yield the raw chunk as-is; caller decides how to interpret
                        yield raw_chunk
            except httpx.HTTPError as exc:
                # surface an error as a final chunk to allow the stream to finish gracefully
                yield json.dumps({"error": str(exc)})


class DummyLLMClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    async def stream(self, prompt: str):
        # Minimal placeholder generator that yields a few chunks
        for part in ["Thinking...", f"Review for: {prompt}", "Final sentence."]:
            await asyncio.sleep(0.1)
            yield part


def get_llm_client() -> Any:
    # Prefer HTTP stream client targeting settings.langgraph_endpoint.
    endpoint = getattr(settings, "langgraph_endpoint", None)
    api_key = getattr(settings, "lmstudio_api_key", None)
    if endpoint:
        return HTTPStreamLLMClient(endpoint=endpoint, api_key=api_key)
    return DummyLLMClient(api_key=api_key)
