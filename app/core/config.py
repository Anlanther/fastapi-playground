from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI Playground"
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/testdb"
    allow_origins: list[str] = ["http://localhost:4200"]
    # LangGraph / LM Studio settings
    llm_provider: str | None = None
    lmstudio_api_key: str | None = None
    langgraph_endpoint: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
