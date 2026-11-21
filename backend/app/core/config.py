from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = Field(default="Ecommerce Price Intelligence")
    app_env: str = Field(default="development")
    api_v1_prefix: str = Field(default="/api/v1")
    database_url: str = Field(default=f"sqlite:///{BASE_DIR / 'app.db'}")
    secret_key: str = Field(default="dev-secret-key")
    api_key: str = Field(default="dev-local-key")
    auth_required: bool = Field(default=False)
    base_currency: str = Field(default="USD")
    scheduler_timezone: str = Field(default="UTC")
    collection_interval_minutes: int = Field(default=60)

    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
