from __future__ import annotations

import json
from datetime import UTC, date, datetime

import pytest

from seoul_mens_daily_edit.images.domain import CompositionPreset, ReferenceImage
from seoul_mens_daily_edit.images.policy import (
    STYLE_ART_DIRECTION_PREFERENCES,
    STYLE_COMPOSITION_PREFERENCES,
    STYLE_SCENES,
    select_art_direction,
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


def build_prompt(style: StylePreset, composition: CompositionPreset):
    target_date = date(2026, 8, 20)
    weather = make_weather_snapshot(target_date)
    selection = make_selection(target_date, style)
    recipe = build_recipe_candidates(weather, selection)[0]
    scene = select_scene(style, target_date, [])
    art_direction = select_art_direction(style, target_date, [], composition)
    prompt = ImagePromptBuilder().build(
        weather,
        selection,
        recipe,
        composition,
        scene=scene,
        art_direction=art_direction,
    )
    return recipe, prompt


@pytest.mark.parametrize("style", list(StylePreset))
def test_prompt_builder_maps_every_style_to_provider_neutral_and_flux_prompt(
    style: StylePreset,
) -> None:
    recipe, prompt = build_prompt(style, CompositionPreset.FACELESS_HERO)

    assert recipe.top.description in prompt.text
    assert "temperature band mild" in prompt.text
    assert prompt.text.startswith("Vertical 4:5 men's fashion editorial photographed strictly")
    assert "Only the clothed body below the neck is inside the visible composition" in prompt.text
    assert "Silhouette relationship:" in prompt.text
    assert "Pose and art direction:" in prompt.text
    assert style.value.replace("_", " ").lower() in prompt.text
    assert prompt.flux_structured_text is not None
    flux_document = json.loads(prompt.flux_structured_text)
    assert flux_document["composition"].startswith("Vertical 4:5 men's fashion editorial")
    assert recipe.top.description in flux_document["subjects"][0]["description"]
    assert flux_document["art_direction"]["preset"] == prompt.art_direction.preset.value


@pytest.mark.parametrize(
    ("composition", "required_phrases"),
    [
        (
            CompositionPreset.FACELESS_HERO,
            (
                "Vertical 4:5 men's fashion editorial photographed strictly from the base "
                "of the neck",
                "Only the clothed body below the neck is inside the visible composition",
                "complete outfit and shoes visible",
            ),
        ),
        (
            CompositionPreset.EDITORIAL_CROP,
            (
                "Vertical 4:5 men's fashion editorial photographed strictly from the base "
                "of the neck",
                "Only the clothed body below the neck is inside the visible composition",
                "the outfit is the visual subject",
            ),
        ),
        (
            CompositionPreset.REAR,
            ("back of the head may remain in frame", "face remains invisible"),
        ),
        (
            CompositionPreset.THREE_QUARTER_REAR,
            ("only the back of the head is visible", "no facial profile is visible"),
        ),
        (
            CompositionPreset.STREET_SNAP,
            (
                "entire head is completely outside the top edge of the frame",
                "upper boundary intersects at the base of the neck",
                "entire face remains invisible",
            ),
        ),
        (
            CompositionPreset.DETAIL_EDITORIAL,
            ("accessories, fabric, and footwear below the neck", "no head or face region"),
        ),
    ],
)
def test_prompt_builder_applies_composition_specific_faceless_framing(
    composition: CompositionPreset,
    required_phrases: tuple[str, ...],
) -> None:
    _, prompt = build_prompt(StylePreset.SOFT_BOYFRIEND, composition)

    for phrase in required_phrases:
        assert phrase in prompt.text


@pytest.mark.parametrize("style", [StylePreset.SOFT_BOYFRIEND, StylePreset.MINIMAL])
def test_front_facing_styles_begin_with_neck_down_framing(style: StylePreset) -> None:
    _, prompt = build_prompt(style, CompositionPreset.FACELESS_HERO)

    assert prompt.text.startswith(
        "Vertical 4:5 men's fashion editorial photographed strictly from the base of the neck "
        "down to the shoes."
    )


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
            scene=select_scene(StylePreset.MINIMAL, target_date, []),
            art_direction=select_art_direction(
                StylePreset.MINIMAL, target_date, [], CompositionPreset.FACELESS_HERO
            ),
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
            scene=select_scene(StylePreset.MINIMAL, target_date, []),
            art_direction=select_art_direction(
                StylePreset.MINIMAL, target_date, [], CompositionPreset.FACELESS_HERO
            ),
        )


@pytest.mark.parametrize("style", list(StylePreset))
def test_policy_uses_style_specific_composition_scene_and_art_direction(style: StylePreset) -> None:
    target_date = date(2026, 8, 20)
    composition = select_composition(style, target_date, [])
    scene = select_scene(style, target_date, [])
    direction = select_art_direction(style, target_date, [], composition)

    assert composition in STYLE_COMPOSITION_PREFERENCES[style]
    assert composition is not CompositionPreset.DETAIL_EDITORIAL
    assert scene in STYLE_SCENES[style]
    assert direction.preset in STYLE_ART_DIRECTION_PREFERENCES[style]
    assert 65 <= direction.outfit_frame_occupancy <= 80


def test_policy_avoids_recent_composition_scene_and_art_direction_when_possible() -> None:
    target_date = date(2026, 8, 20)
    first_composition = select_composition(StylePreset.AMEKAJI, target_date, [])
    second_composition = select_composition(StylePreset.AMEKAJI, target_date, [first_composition])
    first_scene = select_scene(StylePreset.AMEKAJI, target_date, [])
    second_scene = select_scene(StylePreset.AMEKAJI, target_date, [first_scene])
    first_direction = select_art_direction(StylePreset.AMEKAJI, target_date, [], first_composition)
    second_direction = select_art_direction(
        StylePreset.AMEKAJI, target_date, [first_direction.preset], second_composition
    )

    assert second_composition is not first_composition
    assert second_scene is not first_scene
    assert second_direction.preset is not first_direction.preset


def test_otaku_prompt_uses_concrete_content_axis_and_tonal_grammar() -> None:
    recipe, prompt = build_prompt(StylePreset.OTAKU_GRUNGE, CompositionPreset.FACELESS_HERO)

    assert recipe.content_axis is not None
    assert recipe.content_axis.value.replace("_", " ") in prompt.text
    assert "washed, faded, matte, or distressed tonal separation" in prompt.text
    assert "generic cargo" not in prompt.text.lower()
    assert "flannel" not in prompt.text.lower()


def test_prompt_builder_uses_positive_relaxed_trouser_drape_and_soft_waist_policy() -> None:
    _, prompt = build_prompt(StylePreset.SOFT_BOYFRIEND, CompositionPreset.FACELESS_HERO)

    assert "clean front rise" in prompt.text
    assert "smooth uninterrupted drape from the waistband" in prompt.text
    assert "sufficient ease through the upper trouser" in prompt.text
    assert "regular-relaxed upper hangs with soft ease" in prompt.text
    assert "waist hardware stays quiet" in prompt.text


def test_otaku_hero_policy_prioritizes_front_facing_compositions_and_off_center_direction() -> None:
    preferences = STYLE_COMPOSITION_PREFERENCES[StylePreset.OTAKU_GRUNGE]

    assert preferences == (
        CompositionPreset.FACELESS_HERO,
        CompositionPreset.EDITORIAL_CROP,
        CompositionPreset.STREET_SNAP,
    )
    direction = select_art_direction(
        StylePreset.OTAKU_GRUNGE,
        date(2026, 8, 29),
        [],
        CompositionPreset.FACELESS_HERO,
    )
    assert direction.subject_position.value in {"left_third", "right_third"}
    assert direction.body_angle.value in {"front", "three_quarter", "side"}


def test_art_direction_replaces_static_centered_catalog_pose() -> None:
    _, prompt = build_prompt(StylePreset.OTAKU_GRUNGE, CompositionPreset.FACELESS_HERO)
    flux_document = json.loads(prompt.flux_structured_text or "{}")

    assert "natural relaxed standing pose" not in prompt.text
    assert flux_document["subjects"][0]["position"] != "centered with the outfit fully readable"
    assert prompt.art_direction.negative_space.value in {"left", "right", "upper", "environmental"}


def test_reference_conditioned_prompt_front_loads_copy_safe_reference_use_then_faceless() -> None:
    target_date = date(2026, 8, 20)
    weather = make_weather_snapshot(target_date)
    selection = make_selection(target_date, StylePreset.SOFT_BOYFRIEND)
    recipe = build_recipe_candidates(weather, selection)[0]
    prompt = ImagePromptBuilder().build(
        weather,
        selection,
        recipe,
        CompositionPreset.FACELESS_HERO,
        scene=select_scene(StylePreset.SOFT_BOYFRIEND, target_date, []),
        art_direction=select_art_direction(
            StylePreset.SOFT_BOYFRIEND, target_date, [], CompositionPreset.FACELESS_HERO
        ),
        reference_images=(ReferenceImage(filename="soft-street.png", content=b"png"),),
    )

    assert prompt.text.startswith("Use the reference images only for visual grammar:")
    assert prompt.text.splitlines()[1].startswith(
        "Vertical 4:5 men's fashion editorial photographed strictly from the base of the neck"
    )
    assert "Do not reproduce the specific garments, graphics, logos or person." in prompt.text
    flux_document = json.loads(prompt.flux_structured_text or "{}")
    assert flux_document["reference_use"].startswith("Use the reference images only")


def test_prompt_exposes_controlled_garment_structure_texture_and_footwear_shape() -> None:
    recipe, prompt = build_prompt(StylePreset.OTAKU_GRUNGE, CompositionPreset.FACELESS_HERO)

    assert recipe.top.structure.value.replace("_", " ") in prompt.text
    assert recipe.bottom.structure.value.replace("_", " ") in prompt.text
    assert recipe.shoes.shape.value.replace("_", " ") in prompt.text
    assert all(
        profile.value.replace("_", " ") in prompt.text for profile in recipe.texture_profiles
    )
