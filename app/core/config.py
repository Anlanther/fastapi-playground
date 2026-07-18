from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI Playground"
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/testdb"
    allow_origins: list[str] = ["http://localhost:4200"]

    lm_endpoint: str = "http://localhost:1234/v1"
    lm_max_retries: int = 3

    router_model: str = "qwen3.5-9b"
    research_model: str = "qwen3.5-9b"
    approval_model: str = "qwen3.5-9b"

    router_provider: str = "lm_studio"
    research_provider: str = "lm_studio"
    approval_provider: str = "lm_studio"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
