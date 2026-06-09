"""Application settings via Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "IntelliClaim Extractor"
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "json"

    # Security
    secret_key: str = Field(
        default="dev-secret-key-change-in-production-32chars",
        min_length=32,
    )
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    api_keys: str = ""
    rate_limit_per_minute: int = 60

    # Database
    database_url: str = "postgresql+asyncpg://intelliclaim:intelliclaim@localhost:5432/intelliclaim"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Storage
    document_storage_path: str = "/var/lib/intelliclaim/documents"
    max_upload_size_mb: int = 25
    allowed_extensions: str = "pdf,png,jpg,jpeg,tiff,tif"

    # OCR / ML
    tesseract_cmd: str = "/usr/bin/tesseract"
    layoutlm_model_name: str = "microsoft/layoutlmv3-base"
    layoutlm_device: Literal["cpu", "cuda", "mps"] = "cpu"

    # Observability
    otel_enabled: bool = True
    otel_service_name: str = "intelliclaim-extractor"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    prometheus_enabled: bool = True

    @field_validator("api_keys", mode="before")
    @classmethod
    def parse_api_keys(cls, value: str | list[str]) -> str:
        """Normalize API keys to comma-separated string."""
        if isinstance(value, list):
            return ",".join(value)
        return value

    @property
    def api_key_list(self) -> list[str]:
        """Return parsed API key list."""
        if not self.api_keys:
            return []
        return [key.strip() for key in self.api_keys.split(",") if key.strip()]

    @property
    def allowed_extension_list(self) -> list[str]:
        """Return parsed allowed file extensions."""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",") if ext.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        """Return maximum upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()  # type: ignore[call-arg]
