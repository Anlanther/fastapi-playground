from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI Playground"
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/testdb"
    allow_origins: list[str] = ["http://localhost:4200"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
