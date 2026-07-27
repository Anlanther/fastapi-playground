from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.dependencies import get_llm_service
from app.core import Database
from app.dependencies.database import get_db
from app.services import ChatGraphService


class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: str = "default"


router = APIRouter(prefix="/chat-graph", tags=["Chat Graph"])


@router.post("/stream")
async def chat_stream(request: ChatRequest, req: Request):
    db: Database = await get_db(req)
    service = ChatGraphService(db, get_llm_service())

    try:
        initial_state = await service.build_initial_state(
            message=request.message,
            session_id=request.session_id,
            user_id=request.user_id,
        )
    except (OSError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=500, detail=f"DB error: {exc}") from exc

    async def event_stream():
        try:
            async for payload in service.stream_graph(initial_state):
                yield payload
        except (OSError, ValueError, RuntimeError) as exc:
            yield f'{{"error": "{exc}"}}\n'

    return StreamingResponse(event_stream(), media_type="text/event-stream")
