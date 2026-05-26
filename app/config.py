from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Distributed URL Shortener"
    environment: str = "development"
    base_url: str = "http://localhost:8080"
    database_url: str = "sqlite:///./shortener.db"
    redis_url: str | None = None
    cache_ttl_seconds: int = 3600
    default_expiration_days: int = 30
    worker_id: int = Field(default=1, ge=0, le=1023)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

