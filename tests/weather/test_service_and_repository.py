from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from seoul_mens_daily_edit.db.base import Base
from seoul_mens_daily_edit.weather.domain import WeatherCondition, WeatherSnapshot
from seoul_mens_daily_edit.weather.models import WeatherSnapshotRecord
from seoul_mens_daily_edit.weather.repository import WeatherSnapshotRepository
from seoul_mens_daily_edit.weather.service import get_tomorrow_date, get_tomorrow_weather


def make_snapshot(target_date: date, *, high_temperature_c: float = 24.0) -> WeatherSnapshot:
    return WeatherSnapshot(
        target_date=target_date,
        weather_condition=WeatherCondition.CLEAR,
        high_temperature_c=high_temperature_c,
        low_temperature_c=13.0,
        precipitation_probability=10.0,
        fetched_at=datetime(2026, 8, 19, 10, tzinfo=UTC),
    )


class FakeWeatherProvider:
    def __init__(self, snapshot: WeatherSnapshot) -> None:
        self.snapshot = snapshot
        self.requested_target_date: date | None = None

    def fetch_daily_forecast(self, target_date: date) -> WeatherSnapshot:
        self.requested_target_date = target_date
        return self.snapshot


def test_get_tomorrow_date_uses_asia_seoul_boundary() -> None:
    now = datetime(2026, 8, 20, 15, 30, tzinfo=UTC)

    assert get_tomorrow_date(now) == date(2026, 8, 22)


def test_get_tomorrow_weather_persists_and_refreshes_one_target_date() -> None:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker[Session](bind=engine, expire_on_commit=False)
    Base.metadata.create_all(engine)
    repository = WeatherSnapshotRepository(session_factory)
    target_date = date(2026, 8, 22)
    provider = FakeWeatherProvider(make_snapshot(target_date))

    try:
        saved = get_tomorrow_weather(
            provider,
            repository,
            now=datetime(2026, 8, 20, 15, 30, tzinfo=UTC),
        )
        refreshed = repository.save(make_snapshot(target_date, high_temperature_c=27.0))

        with session_factory() as session:
            count = session.scalar(select(func.count()).select_from(WeatherSnapshotRecord))

        assert provider.requested_target_date == target_date
        assert saved.target_date == target_date
        assert refreshed.high_temperature_c == 27.0
        assert count == 1
        assert repository.get_by_target_date(target_date).high_temperature_c == 27.0
    finally:
        engine.dispose()


def test_get_tomorrow_weather_rejects_wrong_target_date() -> None:
    engine = create_engine("sqlite+pysqlite://", poolclass=StaticPool)
    session_factory = sessionmaker[Session](bind=engine)
    Base.metadata.create_all(engine)
    repository = WeatherSnapshotRepository(session_factory)
    provider = FakeWeatherProvider(make_snapshot(date(2026, 8, 21)))

    try:
        with pytest.raises(ValueError, match="target_date"):
            get_tomorrow_weather(
                provider,
                repository,
                now=datetime(2026, 8, 20, 15, 30, tzinfo=UTC),
            )
    finally:
        engine.dispose()
