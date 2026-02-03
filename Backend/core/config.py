"""
Application configuration using Pydantic v2 settings.
Production-safe for Vercel.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal, List

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


_BACKEND_DIR = Path(__file__).resolve().parents[1]
_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # -------------------------
    # API
    # -------------------------
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    api_title: str = Field(default="Choose Your Own Adventure API", alias="API_TITLE")
    api_version: str = Field(default="1.0.0", alias="API_VERSION")

    # -------------------------
    # Environment
    # -------------------------
    environment: Literal["development", "staging", "production"] = Field(
        default="development", alias="ENVIRONMENT"
    )
    debug: bool = Field(default=False, alias="DEBUG")

    # -------------------------
    # Security
    # -------------------------
    secret_key: str = Field(..., alias="SECRET_KEY")  # ❗ REQUIRED
    algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # -------------------------
    # CORS
    # -------------------------
    allowed_origins: str = Field(
        default="http://localhost:3000",
        alias="ALLOWED_ORIGINS",
    )

    # -------------------------
    # Database
    # -------------------------
    database_url: str = Field(
        default="sqlite:///./story_teller.db", alias="DATABASE_URL"
    )
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    # -------------------------
    # External APIs
    # -------------------------
    groq_api_key: str = Field("", alias="GROQ_API_KEY")
    groq_model: str = Field(
        default="llama-3.1-8b-instant", alias="GROQ_MODEL"
    )

    # -------------------------
    # Logging
    # -------------------------
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # -------------------------
    # Validators
    # -------------------------
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def normalize_allowed_origins(cls, v):
        if v is None:
            return ""

        if isinstance(v, list):
            return ",".join(v)

        return str(v)

    @model_validator(mode="after")
    def validate_production(self) -> "Settings":
        if self.environment == "production":
            if self.debug:
                raise ValueError("DEBUG must be False in production")

        if not self.secret_key:
            raise ValueError("SECRET_KEY is required")

        if not self.groq_api_key:
            import warnings
            warnings.warn("GROQ_API_KEY is not set")

        return self

    # -------------------------
    # Helpers
    # -------------------------
    def get_allowed_origins(self) -> List[str]:
        """
        Return allowed origins as a list for FastAPI CORS.
        Supports:
        - JSON array
        - comma-separated string
        - single string
        """
        raw = self.allowed_origins.strip()

        if not raw:
            return []

        # JSON list
        if raw.startswith("["):
            return json.loads(raw)

        # Comma-separated
        return [o.strip() for o in raw.split(",") if o.strip()]

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
