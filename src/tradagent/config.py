from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mistral_api_key: str
    mistral_model: str = "mistral-small-latest"
    db_path: str = "./tradagent.db"

    class Config:
        env_file = ".env"
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()
