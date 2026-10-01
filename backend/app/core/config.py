from functools import lru_cache
import os
from dotenv import load_dotenv

from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./companion.db")
    cors_origins: list[str] = os.getenv("CORS_ORIGINS", '["http://localhost:5173", "http://127.0.0.1:5173"]').split(',')
    lmstudio_api_url: str = os.getenv("LMSTUDIO_API_URL", "http://localhost:1234/v1")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
