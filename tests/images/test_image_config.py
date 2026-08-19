from __future__ import annotations

import pytest
from pydantic import ValidationError

from seoul_mens_daily_edit.core.config import Settings


def test_image_settings_default_to_cloudflare_direct_instagram_generation() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://app:testing-password@localhost:5432/test_database",
    )

    assert settings.image_provider == "cloudflare"
    assert settings.cloudflare_image_model == "@cf/black-forest-labs/flux-2-klein-4b"
    assert settings.cloudflare_image_size == "1080x1350"
    assert settings.openai_image_model == "gpt-image-2"
    assert settings.openai_image_size == "1088x1360"


@pytest.mark.parametrize("size", ["1921x2401", "1080x1352", "invalid"])
def test_image_settings_reject_invalid_cloudflare_generation_size(size: str) -> None:
    with pytest.raises(ValidationError, match="cloudflare_image_size"):
        Settings(
            database_url="postgresql+psycopg://app:testing-password@localhost:5432/test_database",
            cloudflare_image_size=size,
        )


@pytest.mark.parametrize("size", ["1024x1536", "1088x1352", "invalid"])
def test_image_settings_reject_invalid_openai_generation_size(size: str) -> None:
    with pytest.raises(ValidationError, match="openai_image_size"):
        Settings(
            database_url="postgresql+psycopg://app:testing-password@localhost:5432/test_database",
            openai_image_size=size,
        )
