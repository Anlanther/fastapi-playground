import asyncio
import json
import os

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import text

from database import Database
from db_models import get_users_table
from mocks import MOCK_RESPONSE_1, MOCK_RESPONSE_2
from models import AgentResponse

# Database Configuration (Uses environment variable or defaults to local)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/testdb"
)

db = Database(DATABASE_URL)

# Register tables
db.register_table('users', get_users_table(db.metadata))

async def get_db():
    async with db.engine.begin() as conn:
        await conn.execute(text("SELECT 1"))  # Verify connection
    yield

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


@app.on_event("startup")
async def startup():
    await db.init_db()


@app.get("/")
async def root():
    return {"message": "FastAPI + PostgreSQL is working!"}


# Streaming endpoints
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


# Database endpoints
@app.post("/users")
async def create_user(username: str, email: str, db_dep=Depends(get_db)):
    try:
        async with db.engine.begin() as conn:
            await conn.execute(
                text("INSERT INTO users (username, email) VALUES (:username, :email)"),
                {"username": username, "email": email}
            )
        return {"message": "User created successfully", "username": username, "email": email}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
