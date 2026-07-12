from fastapi.testclient import TestClient

from app.api.main import api_router


def test_review_requires_book_title():
    client = TestClient(api_router)
    resp = client.post("/react/review", json={})
    assert resp.status_code == 400


def test_review_stream_starts():
    client = TestClient(api_router)
    payload = {"action": "start",
               "book_title": "Test Book", "session_id": "s1"}
    resp = client.post("/react/review", json=payload, stream=True)
    # fast check: status and content-type
    assert resp.status_code == 200
    assert resp.headers.get("content-type", "").startswith("text/event-stream")
