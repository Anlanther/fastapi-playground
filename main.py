import asyncio
import json

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from mocks import MOCK_RESPONSE_1, MOCK_RESPONSE_2
from models import AgentResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def generate_stream(data: list[AgentResponse], delay=0.5):
    for item in data:
        payload = json.dumps(item.model_dump(mode="json")) + "\n"
        yield payload
        await asyncio.sleep(delay)


@app.post("/research")
async def stream_research_response() -> StreamingResponse:
    return StreamingResponse(
        generate_stream(MOCK_RESPONSE_1), media_type="text/event-stream"
    )


@app.post("/core")
async def stream_core_response() -> StreamingResponse:
    return StreamingResponse(
        generate_stream(MOCK_RESPONSE_2), media_type="text/event-stream"
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
