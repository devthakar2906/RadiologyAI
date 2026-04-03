from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "Radiology AI"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = Field(default="change-me-super-secret-key", alias="SECRET_KEY")
    access_token_expire_minutes: int = 60 * 24
    algorithm: str = "HS256"
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/radiology_ai",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    celery_broker_url: str = Field(default="redis://localhost:6379/1", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND")
    encryption_key: str = Field(
        default="MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=",
        alias="ENCRYPTION_KEY",
    )
    stt_model: str = Field(default="google/medasr", alias="STT_MODEL")
    summarization_model: str = Field(
        default="Falconsai/medical_summarization",
        alias="SUMMARIZATION_MODEL",
    )
    hf_token: str | None = Field(default=None, alias="HF_TOKEN")
    uploads_dir: str = Field(default=str(BASE_DIR / "uploads"), alias="UPLOADS_DIR")
    frontend_url: str = Field(default="http://localhost:9997", alias="FRONTEND_URL")
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    Path(settings.uploads_dir).mkdir(parents=True, exist_ok=True)
    return settings
