from __future__ import annotations

import pytest
from pydantic import ValidationError

from seoul_mens_daily_edit.core.config import (
    CLOUDFLARE_KLEIN_4B_MODEL,
    CLOUDFLARE_KLEIN_9B_MODEL,
    Settings,
)


def test_image_settings_default_to_cloudflare_direct_instagram_generation() -> None:
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://app:testing-password@localhost:5432/test_database",
    )

    assert settings.image_provider == "cloudflare"
    assert settings.cloudflare_image_model == CLOUDFLARE_KLEIN_4B_MODEL
    assert settings.cloudflare_image_size == "1088x1360"
    assert settings.cloudflare_image_guidance is None
    assert settings.cloudflare_image_seed is None
    assert settings.openai_image_model == "gpt-image-2"
    assert settings.openai_image_size == "1088x1360"


@pytest.mark.parametrize("size", ["1921x2401", "1080x1352", "invalid"])
def test_image_settings_reject_invalid_cloudflare_generation_size(size: str) -> None:
    with pytest.raises(ValidationError, match="cloudflare_image_size"):
        Settings(
            _env_file=None,
            database_url="postgresql+psycopg://app:testing-password@localhost:5432/test_database",
            cloudflare_image_size=size,
        )


@pytest.mark.parametrize("size", ["1024x1536", "1088x1352", "invalid"])
def test_image_settings_reject_invalid_openai_generation_size(size: str) -> None:
    with pytest.raises(ValidationError, match="openai_image_size"):
        Settings(
            _env_file=None,
            database_url="postgresql+psycopg://app:testing-password@localhost:5432/test_database",
            openai_image_size=size,
        )


@pytest.mark.parametrize("guidance", [float("nan"), float("inf"), float("-inf")])
def test_image_settings_reject_non_finite_cloudflare_guidance(guidance: float) -> None:
    with pytest.raises(ValidationError, match="cloudflare_image_guidance"):
        Settings(
            _env_file=None,
            database_url="postgresql+psycopg://app:testing-password@localhost:5432/test_database",
            cloudflare_image_guidance=guidance,
        )


def test_image_settings_reject_negative_cloudflare_seed() -> None:
    with pytest.raises(ValidationError, match="cloudflare_image_seed"):
        Settings(
            _env_file=None,
            database_url="postgresql+psycopg://app:testing-password@localhost:5432/test_database",
            cloudflare_image_seed=-1,
        )


def test_image_settings_allow_klein_9b_only_as_an_explicit_model_choice() -> None:
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://app:testing-password@localhost:5432/test_database",
        cloudflare_image_model=CLOUDFLARE_KLEIN_9B_MODEL,
    )

    assert settings.cloudflare_image_model == CLOUDFLARE_KLEIN_9B_MODEL
    assert (
        Settings(
            _env_file=None,
            database_url="postgresql+psycopg://app:testing-password@localhost:5432/test_database",
        ).cloudflare_image_model
        == CLOUDFLARE_KLEIN_4B_MODEL
    )
