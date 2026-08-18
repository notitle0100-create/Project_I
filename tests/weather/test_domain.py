from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from seoul_mens_daily_edit.weather.domain import (
    RAIN_SENSITIVE_PROBABILITY_THRESHOLD,
    TemperatureBand,
    WeatherCondition,
    WeatherSnapshot,
    get_styling_hints,
    get_temperature_band,
)


def make_snapshot(**overrides: object) -> WeatherSnapshot:
    values: dict[str, object] = {
        "target_date": date(2026, 8, 20),
        "weather_condition": WeatherCondition.CLEAR,
        "high_temperature_c": 25.3,
        "low_temperature_c": 14.6,
        "precipitation_probability": 39.0,
        "fetched_at": datetime(2026, 8, 19, 10, tzinfo=UTC),
    }
    values.update(overrides)
    return WeatherSnapshot(**values)


def test_snapshot_calculates_temperature_range_and_styling_hints() -> None:
    snapshot = make_snapshot()

    assert snapshot.temperature_range_c == 10.7
    assert get_styling_hints(snapshot).temperature_band == TemperatureBand.WARM
    assert get_styling_hints(snapshot).layering_recommended is True
    assert get_styling_hints(snapshot).rain_sensitive is False


@pytest.mark.parametrize(
    ("high_temperature_c", "expected"),
    [
        (28, TemperatureBand.VERY_HOT),
        (27, TemperatureBand.WARM),
        (23, TemperatureBand.WARM),
        (22, TemperatureBand.MILD),
        (20, TemperatureBand.MILD),
        (19, TemperatureBand.COOL),
        (17, TemperatureBand.COOL),
        (16, TemperatureBand.CHILLY),
        (12, TemperatureBand.CHILLY),
        (11, TemperatureBand.COLD),
        (9, TemperatureBand.COLD),
        (8, TemperatureBand.VERY_COLD),
        (5, TemperatureBand.VERY_COLD),
        (4, TemperatureBand.FREEZING),
    ],
)
def test_temperature_band_boundaries(high_temperature_c: float, expected: TemperatureBand) -> None:
    assert get_temperature_band(high_temperature_c) == expected


def test_rain_threshold_is_inclusive() -> None:
    snapshot = make_snapshot(precipitation_probability=RAIN_SENSITIVE_PROBABILITY_THRESHOLD)

    assert get_styling_hints(snapshot).rain_sensitive is True
