from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import Protocol
from zoneinfo import ZoneInfo

from seoul_mens_daily_edit.weather.domain import SEOUL_TIMEZONE, WeatherSnapshot
from seoul_mens_daily_edit.weather.repository import WeatherSnapshotRepository


class DailyWeatherProvider(Protocol):
    def fetch_daily_forecast(self, target_date: date) -> WeatherSnapshot: ...


def get_tomorrow_weather(
    provider: DailyWeatherProvider,
    repository: WeatherSnapshotRepository,
    *,
    now: datetime | None = None,
) -> WeatherSnapshot:
    target_date = get_tomorrow_date(now)
    snapshot = provider.fetch_daily_forecast(target_date)
    if snapshot.target_date != target_date:
        raise ValueError("provider forecast target_date does not match tomorrow in Asia/Seoul")
    return repository.save(snapshot)


def get_tomorrow_date(now: datetime | None = None) -> date:
    current_time = now or datetime.now(UTC)
    if current_time.tzinfo is None or current_time.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    return current_time.astimezone(ZoneInfo(SEOUL_TIMEZONE)).date() + timedelta(days=1)
