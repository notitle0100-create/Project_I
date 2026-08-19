from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import date

from seoul_mens_daily_edit.styling.domain import Mood, Occasion, StylePreset
from seoul_mens_daily_edit.weather.domain import (
    TemperatureBand,
    WeatherSnapshot,
    get_styling_hints,
)

STYLE_ROTATION: tuple[StylePreset, ...] = (
    StylePreset.SOFT_BOYFRIEND,
    StylePreset.MINIMAL,
    StylePreset.AMEKAJI,
    StylePreset.OTAKU_GRUNGE,
)
RECENT_SELECTION_LIMIT = 8

STYLE_OCCASIONS: dict[StylePreset, tuple[Occasion, ...]] = {
    StylePreset.SOFT_BOYFRIEND: (
        Occasion.DAILY,
        Occasion.CAFE,
        Occasion.DATE,
        Occasion.UNIVERSITY,
        Occasion.NEIGHBORHOOD,
    ),
    StylePreset.MINIMAL: (
        Occasion.LIGHT_WORK,
        Occasion.EXHIBITION,
        Occasion.CAFE,
        Occasion.DATE,
        Occasion.DAILY,
    ),
    StylePreset.AMEKAJI: (
        Occasion.WEEKEND,
        Occasion.TRAVEL,
        Occasion.NEIGHBORHOOD,
        Occasion.CAFE,
        Occasion.DAILY,
    ),
    StylePreset.OTAKU_GRUNGE: (
        Occasion.EXHIBITION,
        Occasion.CAFE,
        Occasion.WEEKEND,
        Occasion.NEIGHBORHOOD,
        Occasion.TRAVEL,
    ),
}

STYLE_MOODS: dict[StylePreset, tuple[Mood, ...]] = {
    StylePreset.SOFT_BOYFRIEND: (Mood.SOFT, Mood.CLEAN, Mood.RELAXED),
    StylePreset.MINIMAL: (Mood.CLEAN, Mood.URBAN, Mood.RELAXED),
    StylePreset.AMEKAJI: (Mood.VINTAGE, Mood.RUGGED, Mood.URBAN),
    StylePreset.OTAKU_GRUNGE: (Mood.DARK, Mood.EXPERIMENTAL, Mood.URBAN),
}

OUTDOOR_HEAVY_OCCASIONS = frozenset({Occasion.WEEKEND, Occasion.TRAVEL})
HEAVY_MOODS = frozenset({Mood.RUGGED})
SUMMER_LIKE_MOODS = frozenset({Mood.SOFT, Mood.RELAXED})


def get_rotated_style(selection_count: int) -> StylePreset:
    if selection_count < 0:
        raise ValueError("selection_count must not be negative")
    return STYLE_ROTATION[selection_count % len(STYLE_ROTATION)]


def select_occasion_and_mood(
    *,
    style: StylePreset,
    target_date: date,
    weather_snapshot: WeatherSnapshot,
    recent_combinations: Iterable[tuple[StylePreset, Occasion, Mood]],
) -> tuple[Occasion, Mood]:
    hints = get_styling_hints(weather_snapshot)
    occasions = list(STYLE_OCCASIONS[style])
    moods = list(STYLE_MOODS[style])

    if hints.rain_sensitive:
        occasions = [occasion for occasion in occasions if occasion not in OUTDOOR_HEAVY_OCCASIONS]
    if hints.temperature_band is TemperatureBand.VERY_HOT:
        moods = [mood for mood in moods if mood not in HEAVY_MOODS]
    if hints.temperature_band is TemperatureBand.FREEZING:
        moods = [mood for mood in moods if mood not in SUMMER_LIKE_MOODS]

    if not occasions or not moods:
        raise ValueError("weather policy removed every occasion or mood candidate")

    recent = set(recent_combinations)
    occasion_candidates = _rotate(occasions, target_date.toordinal())
    mood_candidates = _rotate(moods, target_date.toordinal() + STYLE_ROTATION.index(style))
    for occasion in occasion_candidates:
        for mood in mood_candidates:
            if (style, occasion, mood) not in recent:
                return occasion, mood

    return occasion_candidates[0], mood_candidates[0]


def _rotate(
    values: Sequence[Occasion] | Sequence[Mood], offset: int
) -> list[Occasion] | list[Mood]:
    index = offset % len(values)
    return list(values[index:]) + list(values[:index])
