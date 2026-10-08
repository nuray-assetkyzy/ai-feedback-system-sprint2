from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret_key: str = "dev-secret-change-in-production"
    admin_username: str = "admin"
    admin_password: str = "1234"
    database_url: str = f"sqlite:///{BACKEND_DIR / 'feedback.db'}"
    cors_origins: str = "http://127.0.0.1:8000,http://localhost:8000"
    session_cookie_name: str = "ai_feedback_session"
    session_max_age_seconds: int = 86400
    sentiment_model_id: str = "C:/ai-model-test"
    model_version: str = "xlm-roberta-sentiment-v1 + lingua-v2 + lexicon-intensity-v1"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
