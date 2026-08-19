from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from seoul_mens_daily_edit.outfits.domain import Outerwear, OuterwearCategory, OuterwearFit
from seoul_mens_daily_edit.outfits.policy import (
    MAX_ACCESSORIES_BY_STYLE,
    MAX_RECIPE_CANDIDATES,
    build_recipe_candidates,
    select_recipe_candidate,
)
from seoul_mens_daily_edit.styling.domain import Mood, Occasion, StylePreset, StyleSelection
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


def make_selection(target_date: date, style: StylePreset) -> StyleSelection:
    return StyleSelection(
        target_date=target_date,
        style=style,
        occasion=Occasion.DAILY,
        mood=Mood.CLEAN,
        selected_at=datetime(2026, 8, 19, 10, tzinfo=UTC),
    )


@pytest.mark.parametrize("style", list(StylePreset))
def test_every_style_creates_a_controlled_recipe(style: StylePreset) -> None:
    target_date = date(2026, 8, 20)
    recipe = build_recipe_candidates(
        make_weather_snapshot(target_date), make_selection(target_date, style)
    )[0]

    assert recipe.style is style
    assert len(recipe.palette) <= 3
    assert all(color.value in {item.value for item in recipe.palette} for color in recipe.palette)
    assert len(recipe.accessories) <= MAX_ACCESSORIES_BY_STYLE[style]


def test_hot_weather_excludes_outerwear_and_heavy_top_layers() -> None:
    target_date = date(2026, 8, 20)
    recipes = build_recipe_candidates(
        make_weather_snapshot(target_date, high_temperature_c=30, low_temperature_c=23),
        make_selection(target_date, StylePreset.AMEKAJI),
    )

    assert all(recipe.outer is None for recipe in recipes)
    assert all(
        recipe.top.category.value not in {"knit", "sweatshirt", "hoodie"} for recipe in recipes
    )


def test_freezing_weather_requires_a_warm_outer_layer() -> None:
    target_date = date(2026, 1, 5)
    recipe = build_recipe_candidates(
        make_weather_snapshot(target_date, high_temperature_c=4, low_temperature_c=-3),
        make_selection(target_date, StylePreset.OTAKU_GRUNGE),
    )[0]

    assert recipe.outer is not None
    assert recipe.outer.category is OuterwearCategory.PUFFER
    assert recipe.layering_depth == 3
    assert recipe.top.category.value == "hoodie"
    assert recipe.bottom.category.value == "denim"


def test_rain_sensitive_recipe_includes_a_hem_protection_note() -> None:
    target_date = date(2026, 8, 20)
    recipe = build_recipe_candidates(
        make_weather_snapshot(target_date, precipitation_probability=40),
        make_selection(target_date, StylePreset.MINIMAL),
    )[0]

    assert any("hem" in note.lower() for note in recipe.styling_notes)


def test_large_temperature_range_adds_removable_layer_guidance() -> None:
    target_date = date(2026, 8, 20)
    recipe = build_recipe_candidates(
        make_weather_snapshot(target_date, high_temperature_c=22, low_temperature_c=10),
        make_selection(target_date, StylePreset.OTAKU_GRUNGE),
    )[0]

    assert recipe.outer is not None
    assert any("removed" in note.lower() for note in recipe.styling_notes)


def test_otaku_grunge_uses_original_graphic_language_not_cosplay() -> None:
    target_date = date(2026, 8, 20)
    recipes = build_recipe_candidates(
        make_weather_snapshot(target_date),
        make_selection(target_date, StylePreset.OTAKU_GRUNGE),
    )

    rendered = " ".join(
        text for recipe in recipes for text in (recipe.top.description, *recipe.styling_notes)
    )
    assert "costume" in rendered.lower()
    assert "character" in rendered.lower()
    assert "cosplay" not in rendered.lower()


def test_recent_signature_is_avoided_when_an_alternative_exists() -> None:
    target_date = date(2026, 8, 20)
    weather = make_weather_snapshot(target_date)
    candidates = build_recipe_candidates(
        weather, make_selection(target_date, StylePreset.SOFT_BOYFRIEND)
    )

    selected = select_recipe_candidate(candidates, {candidates[0].signature}, weather)

    assert selected.signature != candidates[0].signature


def test_candidate_selection_has_a_bounded_duplicate_fallback() -> None:
    target_date = date(2026, 8, 20)
    weather = make_weather_snapshot(target_date)
    candidates = build_recipe_candidates(weather, make_selection(target_date, StylePreset.MINIMAL))

    selected = select_recipe_candidate(
        candidates, {candidate.signature for candidate in candidates}, weather
    )

    assert len(candidates) == MAX_RECIPE_CANDIDATES
    assert selected == candidates[0]


def test_invalid_hot_candidate_falls_back_to_next_candidate() -> None:
    target_date = date(2026, 8, 20)
    weather = make_weather_snapshot(target_date, high_temperature_c=30, low_temperature_c=23)
    candidates = list(
        build_recipe_candidates(weather, make_selection(target_date, StylePreset.MINIMAL))
    )
    candidates[0] = candidates[0].model_copy(
        update={
            "outer": Outerwear(
                category=OuterwearCategory.COAT,
                fit=OuterwearFit.REGULAR,
                color="black",
                description="heavy coat",
            ),
            "layering_depth": 2,
        }
    )

    selected = select_recipe_candidate(tuple(candidates), set(), weather)

    assert selected == candidates[1]
