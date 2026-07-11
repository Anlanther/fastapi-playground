import uvicorn
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import text

from app.core import Database
from app.dependencies import get_db as get_db_dependency
from app.dependencies.database import initialize_database
from app.mocks.chat_session_mocks import MOCK_RESPONSE_1, MOCK_RESPONSE_2
from app.services import ChatStreamService

router = APIRouter(tags=["Chat Stream"])


async def startup() -> None:
    """Initialize the database on application startup."""
    db = initialize_database()
    try:
        await db.init_db()
    except Exception:
        return
    finally:
        await db.engine.dispose()


@router.get("/")
async def root():
    return {"message": "FastAPI + PostgreSQL is working!"}


@router.post("/mock-stream-1")
async def stream_research_response() -> StreamingResponse:
    service = ChatStreamService()
    return StreamingResponse(
        service.generate_stream(MOCK_RESPONSE_1),
        media_type="text/event-stream",
    )


@router.post("/mock-stream-2")
async def stream_core_response() -> StreamingResponse:
    service = ChatStreamService()
    return StreamingResponse(
        service.generate_stream(MOCK_RESPONSE_2),
        media_type="text/event-stream",
    )


@router.post("/users")
async def create_user(username: str, email: str, db: Database = Depends(get_db_dependency)):
    try:
        async with db.engine.begin() as conn:
            await conn.execute(
                text("INSERT INTO users (username, email) VALUES (:username, :email)"),
                {"username": username, "email": email},
            )
        return {"message": "User created successfully", "username": username, "email": email}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
