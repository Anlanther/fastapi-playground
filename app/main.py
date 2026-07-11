from fastapi import FastAPI

from app.api.main import create_api_router


def create_app() -> FastAPI:
    return create_api_router()


app = create_app()

__all__ = ["app", "create_app"]
