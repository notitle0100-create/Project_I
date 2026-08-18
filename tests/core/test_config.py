import pytest
from pydantic import ValidationError

from seoul_mens_daily_edit.core.config import Settings


def test_settings_require_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValidationError, match="database_url"):
        Settings(_env_file=None)


def test_settings_accept_postgres_url() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://app:testing-password@localhost:5432/test_database"
    )

    assert settings.database_url.scheme == "postgresql+psycopg"
