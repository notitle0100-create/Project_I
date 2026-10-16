from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from seoul_mens_daily_edit.outfits.domain import OutfitRecipe
from seoul_mens_daily_edit.outfits.policy import (
    MAX_ACCESSORIES_BY_STYLE,
    MAX_RECIPE_CANDIDATES,
    OTAKU_GRUNGE_CONTENT_AXES,
    STYLE_BASES,
    build_recipe_candidates,
    select_recipe_candidate,
    validate_recipe_for_weather,
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
    weather = make_weather_snapshot(target_date)
    recipes = build_recipe_candidates(weather, make_selection(target_date, style))

    assert len(recipes) == MAX_RECIPE_CANDIDATES
    assert all(recipe.style is style for recipe in recipes)
    assert all(len(recipe.palette) <= 3 for recipe in recipes)
    assert all(len(recipe.accessories) <= MAX_ACCESSORIES_BY_STYLE[style] for recipe in recipes)
    assert all(not validate_recipe_for_weather(recipe, weather) for recipe in recipes)
    assert all(recipe.silhouette.lower_volume.value for recipe in recipes)
    assert all(recipe.silhouette.pant_break.value for recipe in recipes)
    assert all(recipe.silhouette.footwear_weight.value for recipe in recipes)


def test_hot_weather_excludes_outerwear_and_heavy_top_layers() -> None:
    target_date = date(2026, 8, 20)
    recipes = build_recipe_candidates(
        make_weather_snapshot(target_date, high_temperature_c=30, low_temperature_c=23),
        make_selection(target_date, StylePreset.AMEKAJI),
    )

    assert all(recipe.outer is None for recipe in recipes)
    assert all(recipe.silhouette.outer_length is None for recipe in recipes)
    assert all(
        recipe.top.category.value not in {"knit", "sweatshirt", "hoodie"} for recipe in recipes
    )


def test_freezing_otaku_recipes_keep_content_axes_without_one_fixed_formula() -> None:
    target_date = date(2026, 1, 5)
    recipes = build_recipe_candidates(
        make_weather_snapshot(target_date, high_temperature_c=4, low_temperature_c=-3),
        make_selection(target_date, StylePreset.OTAKU_GRUNGE),
    )

    assert all(
        recipe.outer is not None and recipe.outer.category.value == "puffer" for recipe in recipes
    )
    assert {recipe.content_axis for recipe in recipes} == set(OTAKU_GRUNGE_CONTENT_AXES)
    assert len({recipe.signature for recipe in recipes}) == len(recipes)


def test_rain_reduces_full_or_stacked_pant_breaks() -> None:
    target_date = date(2026, 8, 20)
    recipes = build_recipe_candidates(
        make_weather_snapshot(target_date, precipitation_probability=40),
        make_selection(target_date, StylePreset.OTAKU_GRUNGE),
    )

    assert all(
        recipe.silhouette.pant_break.value in {"no_break", "slight_break"} for recipe in recipes
    )
    assert all(any("hem" in note.lower() for note in recipe.styling_notes) for recipe in recipes)


def test_large_temperature_range_adds_removable_layer_guidance() -> None:
    target_date = date(2026, 8, 20)
    recipes = build_recipe_candidates(
        make_weather_snapshot(target_date, high_temperature_c=22, low_temperature_c=10),
        make_selection(target_date, StylePreset.OTAKU_GRUNGE),
    )

    assert all(recipe.outer is not None for recipe in recipes)
    assert all(
        any("removed" in note.lower() for note in recipe.styling_notes) for recipe in recipes
    )


def test_soft_boyfriend_uses_soft_proportion_not_one_basic_formula() -> None:
    target_date = date(2026, 8, 20)
    recipes = build_recipe_candidates(
        make_weather_snapshot(target_date), make_selection(target_date, StylePreset.SOFT_BOYFRIEND)
    )

    assert len({recipe.silhouette.strategy for recipe in recipes}) == len(recipes)
    assert all(recipe.silhouette.footwear_weight.value == "light" for recipe in recipes)
    assert all(
        "beige knit + plain denim" not in " ".join(recipe.styling_notes).lower()
        for recipe in recipes
    )
    assert all(recipe.top.fit.value in {"regular", "relaxed"} for recipe in recipes)


def test_soft_boyfriend_rejects_a_fitted_top_recipe() -> None:
    target_date = date(2026, 8, 20)
    recipe = build_recipe_candidates(
        make_weather_snapshot(target_date), make_selection(target_date, StylePreset.SOFT_BOYFRIEND)
    )[0]
    payload = recipe.model_dump(mode="json")
    payload["top"]["fit"] = "fitted"

    with pytest.raises(ValidationError, match="regular or relaxed"):
        OutfitRecipe.model_validate(payload)


def test_minimal_allows_integrated_accessory_details_without_losing_restraint() -> None:
    target_date = date(2026, 8, 20)
    recipes = build_recipe_candidates(
        make_weather_snapshot(target_date), make_selection(target_date, StylePreset.MINIMAL)
    )

    assert MAX_ACCESSORIES_BY_STYLE[StylePreset.MINIMAL] == 2
    assert any(recipe.accessories for recipe in recipes)
    assert all(recipe.silhouette.lower_volume.value in {"straight", "wide"} for recipe in recipes)
    assert all(recipe.silhouette.footwear_weight.value == "medium" for recipe in recipes)


def test_amekaji_uses_contemporary_workwear_proportion_without_costume_stacking() -> None:
    target_date = date(2026, 8, 20)
    recipes = build_recipe_candidates(
        make_weather_snapshot(target_date), make_selection(target_date, StylePreset.AMEKAJI)
    )

    rendered = " ".join(
        part
        for recipe in recipes
        for part in (recipe.top.description, recipe.bottom.description, *recipe.styling_notes)
    ).lower()
    assert all(recipe.silhouette.lower_volume.value in {"relaxed", "wide"} for recipe in recipes)
    assert all(recipe.silhouette.footwear_weight.value in {"medium", "heavy"} for recipe in recipes)
    assert "costume" not in rendered


def test_otaku_grunge_uses_two_content_axes_not_flannel_or_generic_cargo_defaults() -> None:
    target_date = date(2026, 8, 20)
    recipes = build_recipe_candidates(
        make_weather_snapshot(target_date, high_temperature_c=22, low_temperature_c=10),
        make_selection(target_date, StylePreset.OTAKU_GRUNGE),
    )
    rendered = " ".join(
        part
        for recipe in recipes
        for part in (
            recipe.top.description,
            recipe.bottom.description,
            recipe.outer.description if recipe.outer is not None else "",
            *recipe.styling_notes,
        )
    ).lower()

    assert {recipe.content_axis for recipe in recipes} == set(OTAKU_GRUNGE_CONTENT_AXES)
    assert "detailed_dark_top" in rendered
    assert "graphic_focal_top" in rendered
    assert "original abstract" in rendered
    assert "flannel" not in rendered
    assert "cargo" not in rendered
    assert "techwear" not in rendered
    assert "costume" in rendered


def test_otaku_all_black_uses_tonal_texture_and_restrained_hardware() -> None:
    target_date = date(2026, 8, 20)
    recipes = build_recipe_candidates(
        make_weather_snapshot(target_date), make_selection(target_date, StylePreset.OTAKU_GRUNGE)
    )

    all_black = [
        recipe
        for recipe in recipes
        if {"black", "charcoal"}.issubset({color.value for color in recipe.palette})
    ]
    assert all_black
    assert all(len(recipe.accessories) <= 1 for recipe in all_black)
    assert all("texture" in " ".join(recipe.styling_notes).lower() for recipe in all_black)
    assert all(
        accessory.placement is not None and accessory.visual_role.value in {"support", "focal"}
        for recipe in all_black
        for accessory in recipe.accessories
    )
    detailed_dark = [
        recipe for recipe in recipes if recipe.content_axis.value == "detailed_dark_top"
    ]
    assert detailed_dark
    assert all(recipe.bag is None for recipe in detailed_dark)


def test_recipe_signature_tracks_silhouette_diversity() -> None:
    target_date = date(2026, 8, 20)
    weather = make_weather_snapshot(target_date)
    candidates = build_recipe_candidates(
        weather, make_selection(target_date, StylePreset.SOFT_BOYFRIEND)
    )

    selected = select_recipe_candidate(candidates, {candidates[0].signature}, weather)

    assert selected.signature != candidates[0].signature
    assert candidates[0].silhouette.strategy.value in candidates[0].signature
    assert candidates[0].silhouette.pant_break.value in candidates[0].signature


def test_all_oversized_and_heavy_recipe_is_rejected() -> None:
    target_date = date(2026, 8, 20)
    recipe = build_recipe_candidates(
        make_weather_snapshot(target_date, high_temperature_c=22, low_temperature_c=10),
        make_selection(target_date, StylePreset.OTAKU_GRUNGE),
    )[0]
    payload = recipe.model_dump(mode="json")
    payload["top"]["fit"] = "oversized"
    payload["outer"]["fit"] = "oversized"
    payload["silhouette"]["lower_volume"] = "very_wide"
    payload["silhouette"]["footwear_weight"] = "heavy"

    with pytest.raises(ValidationError, match="all oversized"):
        OutfitRecipe.model_validate(payload)


def test_recipe_payload_without_new_fields_remains_readable() -> None:
    target_date = date(2026, 8, 20)
    recipe = build_recipe_candidates(
        make_weather_snapshot(target_date), make_selection(target_date, StylePreset.SOFT_BOYFRIEND)
    )[0]
    payload = recipe.model_dump(mode="json")
    payload.pop("silhouette")
    payload.pop("content_axis")

    restored = OutfitRecipe.model_validate(payload)

    assert restored.silhouette.strategy.value == "straight_balanced"
    assert restored.content_axis is None


def test_candidate_selection_has_a_bounded_duplicate_fallback() -> None:
    target_date = date(2026, 8, 20)
    weather = make_weather_snapshot(target_date)
    candidates = build_recipe_candidates(weather, make_selection(target_date, StylePreset.MINIMAL))

    selected = select_recipe_candidate(
        candidates, {candidate.signature for candidate in candidates}, weather
    )

    assert selected == candidates[0]


def test_soft_recipe_bases_rotate_beyond_the_old_office_casual_formula() -> None:
    bases = STYLE_BASES[StylePreset.SOFT_BOYFRIEND]

    old_formula = {
        ("gray", "navy", "white"),
        ("beige", "indigo", "off_white"),
    }
    assert {
        (base.top.color.value, base.bottom.color.value, base.shoes.color.value) for base in bases
    }.isdisjoint(old_formula)
    assert len({base.top.structure for base in bases}) >= 2
    assert len({base.bottom.structure for base in bases}) >= 3
    assert len({base.shoes.shape for base in bases}) >= 2


def test_otaku_recipe_bases_cover_both_axes_and_four_lower_families() -> None:
    bases = STYLE_BASES[StylePreset.OTAKU_GRUNGE]

    assert {base.content_axis for base in bases} == set(OTAKU_GRUNGE_CONTENT_AXES)
    assert len({base.bottom.structure for base in bases}) >= 4
    assert all(base.bag is None for base in bases)
    assert all(len(base.accessories) <= 1 for base in bases)
    assert all(base.texture_profiles for base in bases)
    assert all(base.shoes.shape.value != "clean_minimal" for base in bases)


def test_otaku_graphic_axis_uses_controlled_graphic_top_and_dark_denim_option() -> None:
    graphic_bases = [
        base
        for base in STYLE_BASES[StylePreset.OTAKU_GRUNGE]
        if base.content_axis is not None and base.content_axis.value == "graphic_focal_top"
    ]

    assert all(base.top.structure.value == "graphic_focal" for base in graphic_bases)
    assert any(base.bottom.structure.value == "relaxed_black_denim" for base in graphic_bases)
    assert all(
        "character depiction" in base.top.description or "focal print" in base.top.description
        for base in graphic_bases
    )
