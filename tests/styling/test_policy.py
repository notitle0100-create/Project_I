from __future__ import annotations

from datetime import UTC, date, datetime

from seoul_mens_daily_edit.styling.domain import Mood, Occasion, StylePreset
from seoul_mens_daily_edit.styling.policy import select_occasion_and_mood
from seoul_mens_daily_edit.weather.domain import WeatherCondition, WeatherSnapshot


def make_weather_snapshot(
    target_date: date,
    *,
    high_temperature_c: float = 22,
    low_temperature_c: float = 12,
    precipitation_probability: float = 10,
) -> WeatherSnapshot:
    return WeatherSnapshot(
        target_date=target_date,
        weather_condition=WeatherCondition.CLEAR,
        high_temperature_c=high_temperature_c,
        low_temperature_c=low_temperature_c,
        precipitation_probability=precipitation_probability,
        fetched_at=datetime(2026, 8, 19, 10, tzinfo=UTC),
    )


def test_rain_avoids_outdoor_heavy_occasions() -> None:
    occasion, _ = select_occasion_and_mood(
        style=StylePreset.AMEKAJI,
        target_date=date(2026, 8, 22),
        weather_snapshot=make_weather_snapshot(date(2026, 8, 22), precipitation_probability=40),
        recent_combinations=set(),
    )

    assert occasion not in {Occasion.WEEKEND, Occasion.TRAVEL}


def test_very_hot_weather_blocks_rugged_mood() -> None:
    _, mood = select_occasion_and_mood(
        style=StylePreset.AMEKAJI,
        target_date=date(2026, 8, 22),
        weather_snapshot=make_weather_snapshot(date(2026, 8, 22), high_temperature_c=28),
        recent_combinations=set(),
    )

    assert mood is not Mood.RUGGED


def test_freezing_weather_blocks_summer_like_moods() -> None:
    _, mood = select_occasion_and_mood(
        style=StylePreset.SOFT_BOYFRIEND,
        target_date=date(2026, 1, 5),
        weather_snapshot=make_weather_snapshot(
            date(2026, 1, 5), high_temperature_c=4, low_temperature_c=-3
        ),
        recent_combinations=set(),
    )

    assert mood not in {Mood.SOFT, Mood.RELAXED}


def test_recent_combination_is_avoided_when_an_alternative_exists() -> None:
    target_date = date(2026, 8, 22)
    weather_snapshot = make_weather_snapshot(target_date)
    first_choice = select_occasion_and_mood(
        style=StylePreset.MINIMAL,
        target_date=target_date,
        weather_snapshot=weather_snapshot,
        recent_combinations=set(),
    )

    choice = select_occasion_and_mood(
        style=StylePreset.MINIMAL,
        target_date=target_date,
        weather_snapshot=weather_snapshot,
        recent_combinations={(StylePreset.MINIMAL, *first_choice)},
    )

    assert choice != first_choice
