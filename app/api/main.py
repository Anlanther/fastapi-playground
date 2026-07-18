import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat_graph, chat_stream, health
from app.core.config import settings
from app.dependencies.database import initialize_database

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application")
    db = initialize_database()
    await db.init_db()
    app.state.db = db
    yield
    await db.engine.dispose()
    logger.info("Shutting down application")


def create_api_router() -> FastAPI:
    api_router = FastAPI(lifespan=lifespan, title="FastAPI Playground")
    api_router.include_router(health.router)
    api_router.include_router(chat_stream.router)
    api_router.include_router(chat_graph.router)
    api_router.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return api_router


api_router = create_api_router()
