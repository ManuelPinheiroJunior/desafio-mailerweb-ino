from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = Field(default="meeting-room-backend", alias="APP_NAME")
    environment: str = Field(default="local", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    cors_allowed_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="CORS_ALLOWED_ORIGINS",
    )

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/meeting_room",
        alias="DATABASE_URL",
    )

    jwt_secret_key: str = Field(default="change-me", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=60, alias="JWT_EXPIRE_MINUTES")
    admin_email: str = Field(default="admin@company.local", alias="ADMIN_EMAIL")

    worker_poll_interval_seconds: int = Field(default=3, alias="WORKER_POLL_INTERVAL_SECONDS")
    worker_batch_size: int = Field(default=20, alias="WORKER_BATCH_SIZE")
    worker_max_backoff_seconds: int = Field(default=1800, alias="WORKER_MAX_BACKOFF_SECONDS")
    worker_processing_timeout_seconds: int = Field(
        default=300,
        alias="WORKER_PROCESSING_TIMEOUT_SECONDS",
    )
    email_sender_address: str = Field(
        default="no-reply@meeting-room.local",
        alias="EMAIL_SENDER_ADDRESS",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_cors_origins() -> list[str]:
    raw = get_settings().cors_allowed_origins
    return [origin.strip() for origin in raw.split(",") if origin.strip()]
