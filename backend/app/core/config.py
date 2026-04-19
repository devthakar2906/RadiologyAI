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
    stt_fallback_model: str = Field(default="openai/whisper-large-v3-turbo", alias="STT_FALLBACK_MODEL")
    stt_local_cache_dir: str = Field(default=str(BASE_DIR / ".hf-cache"), alias="STT_LOCAL_CACHE_DIR")
    llm_model: str = Field(default="meta-llama/Llama-3.3-70B-Instruct", alias="LLM_MODEL")
    hf_token: str | None = Field(default=None, alias="HF_TOKEN")
    ffmpeg_path: str | None = Field(default=None, alias="FFMPEG_PATH")
    radreport_base_url: str = Field(default="https://radreport.org", alias="RADREPORT_BASE_URL")
    template_cache_dir: str = Field(default=str(BASE_DIR / "templates"), alias="TEMPLATE_CACHE_DIR")
    uploads_dir: str = Field(default=str(BASE_DIR / "uploads"), alias="UPLOADS_DIR")
    frontend_url: str = Field(default="http://localhost:9997", alias="FRONTEND_URL")
    celery_worker_concurrency: int = Field(default=4, alias="CELERY_WORKER_CONCURRENCY")
    celery_worker_pool: str = Field(default="prefork", alias="CELERY_WORKER_POOL")
    redis_max_connections: int = Field(default=50, alias="REDIS_MAX_CONNECTIONS")
    hf_request_timeout_seconds: float = Field(default=120.0, alias="HF_REQUEST_TIMEOUT_SECONDS")
    hf_max_retries: int = Field(default=3, alias="HF_MAX_RETRIES")
    transcription_rate_limit_count: int = Field(default=20, alias="TRANSCRIPTION_RATE_LIMIT_COUNT")
    transcription_rate_limit_window_seconds: int = Field(default=300, alias="TRANSCRIPTION_RATE_LIMIT_WINDOW_SECONDS")
    flower_port: int = Field(default=5555, alias="FLOWER_PORT")
    auth_cookie_name: str = Field(default="radiologyai_access_token", alias="AUTH_COOKIE_NAME")
    auth_cookie_secure: bool = Field(default=False, alias="AUTH_COOKIE_SECURE")
    auth_cookie_samesite: str = Field(default="lax", alias="AUTH_COOKIE_SAMESITE")
    auth_rate_limit_count: int = Field(default=10, alias="AUTH_RATE_LIMIT_COUNT")
    auth_rate_limit_window_seconds: int = Field(default=300, alias="AUTH_RATE_LIMIT_WINDOW_SECONDS")
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    Path(settings.uploads_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.template_cache_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.stt_local_cache_dir).mkdir(parents=True, exist_ok=True)
    return settings
