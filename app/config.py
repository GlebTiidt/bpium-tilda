"""Configuration helpers."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Loads environment variables for the integration backend."""

    model_config = SettingsConfigDict(extra="ignore", env_file=".env.local", env_file_encoding="utf-8")

    bpium_domain: str = Field(..., alias="BPIUM_DOMAIN")
    bpium_email: str = Field(..., alias="BPIUM_EMAIL")
    bpium_password: str = Field(..., alias="BPIUM_PASSWORD")

    # Optional Tilda values (можно использовать позже, когда добавим загрузку в Tilda API)
    tilda_public_key: Optional[str] = Field(default=None, alias="TILDA_PUBLIC_KEY")
    tilda_secret_key: Optional[str] = Field(default=None, alias="TILDA_SECRET_KEY")
    tilda_project_id: Optional[str] = Field(default=None, alias="TILDA_PROJECT_ID")
    tilda_page_id: Optional[str] = Field(default=None, alias="TILDA_PAGE_ID")

    cache_ttl_seconds: int = Field(default=300, alias="CACHE_TTL_SECONDS")
    cors_allow_origins: list[str] = Field(default_factory=list, alias="CORS_ALLOW_ORIGINS")

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: str | list[str] | None) -> list[str]:
        if value is None:
            return ["*"]
        if isinstance(value, list):
            return value or ["*"]
        return [origin.strip() for origin in value.split(",") if origin.strip()] or ["*"]


settings = Settings()
