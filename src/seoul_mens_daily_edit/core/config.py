from __future__ import annotations

import math
from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

CLOUDFLARE_KLEIN_4B_MODEL = "@cf/black-forest-labs/flux-2-klein-4b"
CLOUDFLARE_KLEIN_9B_MODEL = "@cf/black-forest-labs/flux-2-klein-9b"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    timezone: str = "Asia/Seoul"
    dry_run: bool = True
    database_url: PostgresDsn

    image_provider: Literal["cloudflare", "openai"] = "cloudflare"
    cloudflare_account_id: str | None = None
    cloudflare_api_token: SecretStr | None = None
    cloudflare_image_model: Literal[
        "@cf/black-forest-labs/flux-2-klein-4b",
        "@cf/black-forest-labs/flux-2-klein-9b",
    ] = CLOUDFLARE_KLEIN_4B_MODEL
    cloudflare_image_size: str = "1088x1360"
    cloudflare_image_guidance: float | None = None
    cloudflare_image_seed: int | None = Field(default=None, ge=0)
    cloudflare_image_timeout_seconds: float = Field(default=60.0, gt=0)

    openai_api_key: SecretStr | None = None
    openai_image_model: str = "gpt-image-2"
    openai_image_quality: Literal["low", "medium", "high", "auto"] = "medium"
    openai_image_size: str = "1088x1360"
    generated_images_dir: str = "data/generated"
    openai_image_timeout_seconds: float = Field(default=60.0, gt=0)

    @field_validator("openai_image_size")
    @classmethod
    def validate_openai_image_size(cls, value: str) -> str:
        try:
            width_text, height_text = value.lower().split("x", maxsplit=1)
            width, height = int(width_text), int(height_text)
        except ValueError as exc:
            raise ValueError("openai_image_size must use WIDTHxHEIGHT") from exc
        if width % 16 != 0 or height % 16 != 0:
            raise ValueError("openai_image_size dimensions must be multiples of 16")
        if width * 5 != height * 4:
            raise ValueError("openai_image_size must use a 4:5 aspect ratio")
        return value

    @field_validator("cloudflare_image_size")
    @classmethod
    def validate_cloudflare_image_size(cls, value: str) -> str:
        try:
            width_text, height_text = value.lower().split("x", maxsplit=1)
            width, height = int(width_text), int(height_text)
        except ValueError as exc:
            raise ValueError("cloudflare_image_size must use WIDTHxHEIGHT") from exc
        if not 256 <= width <= 1920 or not 256 <= height <= 1920:
            raise ValueError("cloudflare_image_size dimensions must be between 256 and 1920")
        if width * 5 != height * 4:
            raise ValueError("cloudflare_image_size must use a 4:5 aspect ratio")
        return value

    @field_validator("cloudflare_image_guidance")
    @classmethod
    def validate_cloudflare_image_guidance(cls, value: float | None) -> float | None:
        if value is not None and not math.isfinite(value):
            raise ValueError("cloudflare_image_guidance must be a finite float")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
