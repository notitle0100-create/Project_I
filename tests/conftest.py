from __future__ import annotations

import pytest

from seoul_mens_daily_edit.core.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        app_env="test",
        database_url="postgresql+psycopg://app:testing-password@localhost:5432/test_database",
    )
