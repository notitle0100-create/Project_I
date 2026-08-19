from __future__ import annotations

from datetime import UTC, date, datetime

from seoul_mens_daily_edit.styling.domain import StyleSelection
from seoul_mens_daily_edit.styling.policy import (
    RECENT_SELECTION_LIMIT,
    get_rotated_style,
    select_occasion_and_mood,
)
from seoul_mens_daily_edit.styling.repository import StyleSelectionRepository
from seoul_mens_daily_edit.weather.domain import WeatherSnapshot


def select_style_context(
    target_date: date,
    weather_snapshot: WeatherSnapshot,
    repository: StyleSelectionRepository,
    *,
    selected_at: datetime | None = None,
) -> StyleSelection:
    if isinstance(target_date, datetime):
        raise ValueError("target_date must be a date, not a datetime")
    if not isinstance(target_date, date):
        raise ValueError("target_date must be a date")
    if not isinstance(weather_snapshot, WeatherSnapshot):
        raise ValueError("weather_snapshot must be a WeatherSnapshot")
    if weather_snapshot.target_date != target_date:
        raise ValueError("weather_snapshot target_date must match target_date")

    existing = repository.get_by_target_date(target_date)
    if existing is not None:
        return existing

    style = get_rotated_style(repository.count())
    recent = repository.get_recent(RECENT_SELECTION_LIMIT)
    occasion, mood = select_occasion_and_mood(
        style=style,
        target_date=target_date,
        weather_snapshot=weather_snapshot,
        recent_combinations={(item.style, item.occasion, item.mood) for item in recent},
    )
    return repository.get_or_create(
        StyleSelection(
            target_date=target_date,
            style=style,
            occasion=occasion,
            mood=mood,
            selected_at=selected_at or datetime.now(UTC),
        )
    )
