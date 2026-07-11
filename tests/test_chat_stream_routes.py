from fastapi.testclient import TestClient

from app.api.main import api_router
from app.dependencies.database import initialize_database
from app.main import create_app


def test_chat_stream_root_is_registered_once():
    paths = [
        route.path for route in api_router.routes if hasattr(route, "path")]

    assert "/chat-stream/" in paths
    assert "/chat-stream/chat-stream/" not in paths


def test_create_app_exposes_chat_stream_routes():
    app = create_app()
    client = TestClient(app)

    response = client.get("/chat-stream/")

    assert response.status_code == 200
    assert response.json() == {"message": "FastAPI + PostgreSQL is working!"}


def test_initialize_database_registers_users_table():
    db = initialize_database()

    assert "users" in db.tables
