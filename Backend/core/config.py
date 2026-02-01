"""Application configuration using Pydantic v2 settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


_BACKEND_DIR = Path(__file__).resolve().parents[1]
_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        # Use an absolute path so running from repo root still loads Backend/.env
        # In production (Vercel), this file won't exist and env vars come from dashboard
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # API Configuration
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    api_title: str = Field(default="Choose Your Own Adventure API", alias="API_TITLE")
    api_version: str = Field(default="1.0.0", alias="API_VERSION")
    
    # Environment
    environment: Literal["development", "staging", "production"] = Field(
        default="development", alias="ENVIRONMENT"
    )
    debug: bool = Field(default=True, alias="DEBUG")
    
    # Security
    allowed_origins: str = Field(
        default="http://localhost:3000",
        alias="ALLOWED_ORIGINS",
        description="Comma-separated list of allowed CORS origins"
    )
    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    
    # External APIs
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    # Default model; can be overridden via GEMINI_MODEL in Backend/.env
    gemini_model: str = Field(default="gemini-2.5-flash-lite", alias="GEMINI_MODEL")
    
    # Database
    database_url: str = Field(default="sqlite:///./story_teller.db", alias="DATABASE_URL")
    db_echo: bool = Field(default=False, alias="DB_ECHO")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """Store as string, convert to list when accessed."""
        if isinstance(v, list):
            return ",".join(v)
        return v or "http://localhost:3000"
    
    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Ensure production has proper security settings."""
        if self.environment == "production":
            if self.secret_key == "change-me-in-production":
                raise ValueError("SECRET_KEY must be changed in production")
            if self.debug:
                raise ValueError("DEBUG must be False in production")

        # Allow either GEMINI_API_KEY or GOOGLE_API_KEY (some libraries expect GOOGLE_API_KEY)
        if not self.gemini_api_key and self.google_api_key:
            self.gemini_api_key = self.google_api_key
        return self

    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    def get_allowed_origins(self) -> list[str]:
        """Get allowed origins as a list."""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()