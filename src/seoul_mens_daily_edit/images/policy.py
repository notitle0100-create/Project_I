from __future__ import annotations

from collections.abc import Iterable
from datetime import date

from seoul_mens_daily_edit.images.domain import CompositionPreset
from seoul_mens_daily_edit.styling.domain import StylePreset

RECENT_COMPOSITION_LIMIT = 8
RECENT_SCENE_LIMIT = 8

STYLE_COMPOSITION_PREFERENCES: dict[StylePreset, tuple[CompositionPreset, ...]] = {
    StylePreset.SOFT_BOYFRIEND: (
        CompositionPreset.FACELESS_HERO,
        CompositionPreset.EDITORIAL_CROP,
    ),
    StylePreset.MINIMAL: (
        CompositionPreset.FACELESS_HERO,
        CompositionPreset.EDITORIAL_CROP,
    ),
    StylePreset.AMEKAJI: (
        CompositionPreset.FACELESS_HERO,
        CompositionPreset.REAR,
        CompositionPreset.THREE_QUARTER_REAR,
    ),
    StylePreset.OTAKU_GRUNGE: (
        CompositionPreset.FACELESS_HERO,
        CompositionPreset.STREET_SNAP,
        CompositionPreset.REAR,
        CompositionPreset.THREE_QUARTER_REAR,
        CompositionPreset.DETAIL_EDITORIAL,
    ),
}

STYLE_SCENES: dict[StylePreset, tuple[str, ...]] = {
    StylePreset.SOFT_BOYFRIEND: (
        "modern cafe exterior",
        "neutral studio editorial space",
        "clean concrete architecture",
    ),
    StylePreset.MINIMAL: (
        "neutral studio editorial space",
        "clean concrete architecture",
        "quiet urban alley",
    ),
    StylePreset.AMEKAJI: (
        "quiet urban alley",
        "subway-adjacent urban architecture",
        "clean concrete architecture",
    ),
    StylePreset.OTAKU_GRUNGE: (
        "modern Seoul street",
        "subway-adjacent urban architecture",
        "quiet urban alley",
    ),
}


def select_composition(
    style: StylePreset,
    target_date: date,
    recent_compositions: Iterable[CompositionPreset],
    *,
    allow_detail: bool = False,
) -> CompositionPreset:
    candidates = list(STYLE_COMPOSITION_PREFERENCES[style])
    if not allow_detail:
        candidates = [item for item in candidates if item is not CompositionPreset.DETAIL_EDITORIAL]
    return _select_non_repeating(candidates, target_date.toordinal(), set(recent_compositions))


def select_scene(style: StylePreset, target_date: date, recent_scenes: Iterable[str]) -> str:
    return _select_non_repeating(STYLE_SCENES[style], target_date.toordinal(), set(recent_scenes))


def _select_non_repeating[T](values: list[T] | tuple[T, ...], offset: int, recent: set[T]) -> T:
    if not values:
        raise ValueError("at least one candidate is required")
    index = offset % len(values)
    rotated = [*values[index:], *values[:index]]
    for value in rotated:
        if value not in recent:
            return value
    return rotated[0]
