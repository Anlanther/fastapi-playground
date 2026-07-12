# FastAPI Playground

## Run the project

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

## Project structure map

Use this map to quickly find the main app entry points, API routes, and supporting modules.

```text
fastapi-playground/
├── app/
│   ├── main.py                  # App factory and top-level FastAPI instance
│   ├── api/
│   │   ├── main.py              # Creates the API router and wires in routes
│   │   └── routes/
│   │       ├── health.py        # /health and /ready endpoints
│   │       ├── chat_stream.py   # Streaming chat demo routes and startup logic
│   │       └── react.py         # React-style review streaming and approval routes
│   ├── core/
│   │   ├── config.py            # Settings and environment configuration
│   │   └── database.py          # Database wrapper and initialization helpers
│   ├── dependencies/
│   │   └── database.py          # Dependency injection for database access
│   ├── mocks/
│   │   └── chat_session_mocks.py # Mock payloads used by streaming demos
│   ├── models/
│   │   └── chat_session_models.py # Pydantic/SQLAlchemy model definitions
│   └── services/
│       ├── chat_stream_service.py
│       └── react_service.py     # Streaming service logic for chat/react flows
├── data/                        # Local PostgreSQL data directory used in development
├── tests/
│   └── test_chat_stream_routes.py
├── docker-compose.yml           # Local containerized service setup
├── dockerfile                   # Container build instructions
└── pyproject.toml               # Project metadata and Python dependencies
```

## Quick navigation guide

- Start with [app/main.py](app/main.py) if you want the app factory and top-level application object.
- Review [app/api/main.py](app/api/main.py) to see how routers are registered.
- Explore the route handlers in [app/api/routes](app/api/routes) for endpoint behavior.
- Look in [app/services](app/services) for streaming and business logic.
- Use [app/core](app/core) and [app/models](app/models) for shared database/configuration abstractions.
- The [tests](tests) directory contains route-level coverage for the streaming endpoints.
