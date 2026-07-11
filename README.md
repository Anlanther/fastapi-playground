To run project

Option 1 — recommended (uses `uv` helper):

```shell
uv run fastapi dev
```

Option 2 — run `uvicorn` directly:

```shell
uvicorn app.api.main:api_router --reload --host 0.0.0.0 --port 8000
```

Notes:
- The project exposes the FastAPI instance at import path `app.main:app` for some CLIs.
- The ASGI application object used by the repo is `app.api.main:api_router`.
