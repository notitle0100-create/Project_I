from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from seoul_mens_daily_edit.images.domain import CompositionPreset
from seoul_mens_daily_edit.images.policy import (
    STYLE_COMPOSITION_PREFERENCES,
    select_composition,
    select_scene,
)
from seoul_mens_daily_edit.images.prompt_builder import ImagePromptBuilder
from seoul_mens_daily_edit.outfits.policy import build_recipe_candidates
from seoul_mens_daily_edit.styling.domain import Mood, Occasion, StylePreset, StyleSelection
from seoul_mens_daily_edit.weather.domain import WeatherCondition, WeatherSnapshot


def make_weather_snapshot(target_date: date) -> WeatherSnapshot:
    return WeatherSnapshot(
        target_date=target_date,
        weather_condition=WeatherCondition.RAIN,
        high_temperature_c=22,
        low_temperature_c=10,
        precipitation_probability=40,
        fetched_at=datetime(2026, 8, 19, 10, tzinfo=UTC),
    )


def make_selection(target_date: date, style: StylePreset) -> StyleSelection:
    return StyleSelection(
        target_date=target_date,
        style=style,
        occasion=Occasion.DAILY,
        mood=Mood.CLEAN,
        selected_at=datetime(2026, 8, 19, 10, tzinfo=UTC),
    )


@pytest.mark.parametrize("style", list(StylePreset))
def test_prompt_builder_maps_every_style_with_faceless_constraints(style: StylePreset) -> None:
    target_date = date(2026, 8, 20)
    weather = make_weather_snapshot(target_date)
    selection = make_selection(target_date, style)
    recipe = build_recipe_candidates(weather, selection)[0]

    prompt = ImagePromptBuilder().build(
        weather,
        selection,
        recipe,
        CompositionPreset.FACELESS_HERO,
        scene="neutral studio editorial space",
    )

    assert recipe.top.description in prompt.text
    assert "temperature band mild" in prompt.text
    assert "never show a recognizable face" in prompt.text
    assert "eyes, eyebrows, nose, mouth, cheeks, chin, or jawline" in prompt.text
    assert "price labels" in prompt.text
    assert "copyrighted character reproduction" in prompt.text
    assert style.value.replace("_", " ").lower() in prompt.text


def test_prompt_builder_rejects_commercial_recipe_copy() -> None:
    target_date = date(2026, 8, 20)
    weather = make_weather_snapshot(target_date)
    selection = make_selection(target_date, StylePreset.MINIMAL)
    recipe = build_recipe_candidates(weather, selection)[0].model_copy(
        update={"styling_notes": ("Price available on request.",)}
    )

    with pytest.raises(ValueError, match="prohibited commercial copy"):
        ImagePromptBuilder().build(
            weather,
            selection,
            recipe,
            CompositionPreset.FACELESS_HERO,
            scene="neutral studio editorial space",
        )


def test_prompt_builder_rejects_mismatched_context_dates() -> None:
    target_date = date(2026, 8, 20)
    weather = make_weather_snapshot(target_date)
    selection = make_selection(target_date, StylePreset.MINIMAL)
    recipe = build_recipe_candidates(weather, selection)[0].model_copy(
        update={"target_date": date(2026, 8, 21)}
    )

    with pytest.raises(ValueError, match="target_date"):
        ImagePromptBuilder().build(
            weather,
            selection,
            recipe,
            CompositionPreset.FACELESS_HERO,
            scene="neutral studio editorial space",
        )


@pytest.mark.parametrize("style", list(StylePreset))
def test_composition_uses_style_specific_presets(style: StylePreset) -> None:
    composition = select_composition(style, date(2026, 8, 20), [])

    assert composition in STYLE_COMPOSITION_PREFERENCES[style]
    assert composition is not CompositionPreset.DETAIL_EDITORIAL


def test_composition_and_scene_avoid_recent_values_when_possible() -> None:
    target_date = date(2026, 8, 20)
    first_composition = select_composition(StylePreset.AMEKAJI, target_date, [])
    second_composition = select_composition(StylePreset.AMEKAJI, target_date, [first_composition])
    first_scene = select_scene(StylePreset.AMEKAJI, target_date, [])
    second_scene = select_scene(StylePreset.AMEKAJI, target_date, [first_scene])

    assert second_composition is not first_composition
    assert second_scene != first_scene
