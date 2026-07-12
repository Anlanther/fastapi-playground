import uvicorn
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.core import Database
from app.core.config import settings
from app.dependencies import get_db as get_db_dependency
from app.services import ReactService

router = APIRouter(tags=["React"])


def get_database() -> Database:
    db = Database(settings.database_url)
    # Ensure tables registered similarly to other routers
    from app.models import get_session_messages_table, get_users_table

    db.register_table("users", get_users_table(db.metadata))
    db.register_table("session_messages",
                      get_session_messages_table(db.metadata))
    return db


async def startup() -> None:
    db = get_database()
    try:
        await db.init_db()
    except Exception:
        return
    finally:
        await db.engine.dispose()


@router.post("/review")
async def review_book(
    payload: dict = Body(...),
    db: Database = Depends(get_db_dependency),
):
    """Single endpoint that either starts a review stream or records an approval.

    Behavior:
    - To start a review stream: POST {"action": "start", "book_title": "...", "book_author": "...", "session_id": "...", "user_message": "..."}
      returns a `text/event-stream` StreamingResponse.
    - To approve a span: POST {"action": "approve", "session_id": "...", "span_id": "..."}
      returns a JSON confirmation and writes an approved message into `session_messages`.
    """

    action = payload.get("action", "start")
    if action == "approve":
        session_id = payload.get("session_id")
        span_id = payload.get("span_id")
        if not session_id or not span_id:
            raise HTTPException(
                status_code=400, detail="session_id and span_id are required for approval")
        try:
            async with db.engine.begin() as conn:
                await conn.execute(
                    "INSERT INTO session_messages (session_id, role, span_id, approved, payload) VALUES (:session_id, :role, :span_id, :approved, :payload)",
                    {"session_id": session_id, "role": "user", "span_id": span_id,
                        "approved": True, "payload": "user_approved"},
                )
            return {"status": "approved", "session_id": session_id, "span_id": span_id}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    # default: start streaming
    book_title = payload.get("book_title")
    if not book_title:
        raise HTTPException(
            status_code=400, detail="book_title is required to start a review")
    book_author = payload.get("book_author")
    session_id = payload.get("session_id")
    user_message = payload.get("user_message")

    service = ReactService()
    return StreamingResponse(
        service.stream_review(book_title, book_author,
                              session_id, db, user_message=user_message),
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
