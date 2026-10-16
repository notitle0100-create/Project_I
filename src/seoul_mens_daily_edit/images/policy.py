from __future__ import annotations

from collections.abc import Iterable
from datetime import date

from seoul_mens_daily_edit.images.domain import (
    ArtDirection,
    ArtDirectionPreset,
    BackgroundClarity,
    BackgroundTexture,
    BodyAngle,
    CameraDistance,
    CameraHeight,
    CompositionPreset,
    EditorialMood,
    Lighting,
    NegativeSpace,
    Pose,
    ScenePreset,
    SubjectPosition,
)
from seoul_mens_daily_edit.styling.domain import StylePreset

RECENT_COMPOSITION_LIMIT = 8
RECENT_SCENE_LIMIT = 8
RECENT_ART_DIRECTION_LIMIT = 8

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
        CompositionPreset.EDITORIAL_CROP,
        CompositionPreset.STREET_SNAP,
    ),
}

STYLE_SCENES: dict[StylePreset, tuple[ScenePreset, ...]] = {
    StylePreset.SOFT_BOYFRIEND: (
        ScenePreset.SUBDUED_CAFE_EXTERIOR,
        ScenePreset.QUIET_SIDEWALK,
        ScenePreset.CONCRETE_STOREFRONT,
    ),
    StylePreset.MINIMAL: (
        ScenePreset.GLASS_METAL_ARCHITECTURE,
        ScenePreset.TEXTURED_URBAN_WALL,
        ScenePreset.CONCRETE_STOREFRONT,
    ),
    StylePreset.AMEKAJI: (
        ScenePreset.QUIET_SIDEWALK,
        ScenePreset.TEXTURED_URBAN_WALL,
        ScenePreset.PARKING_STRUCTURE,
    ),
    StylePreset.OTAKU_GRUNGE: (
        ScenePreset.NARROW_URBAN_STREET,
        ScenePreset.PARKING_STRUCTURE,
        ScenePreset.TEXTURED_URBAN_WALL,
    ),
}

ART_DIRECTIONS: dict[ArtDirectionPreset, ArtDirection] = {
    ArtDirectionPreset.PINTEREST_STREET: ArtDirection(
        preset=ArtDirectionPreset.PINTEREST_STREET,
        pose=Pose.WEIGHT_SHIFT,
        body_angle=BodyAngle.THREE_QUARTER,
        camera_height=CameraHeight.CHEST,
        camera_distance=CameraDistance.MEDIUM_FULL,
        subject_position=SubjectPosition.RIGHT_THIRD,
        outfit_frame_occupancy=72,
        negative_space=NegativeSpace.LEFT,
        background_texture=BackgroundTexture.SIDEWALK,
        background_clarity=BackgroundClarity.MODERATE,
        lighting=Lighting.SOFT_DAYLIGHT,
        editorial_mood=EditorialMood.CANDID,
    ),
    ArtDirectionPreset.CLEAN_ARCHITECTURAL: ArtDirection(
        preset=ArtDirectionPreset.CLEAN_ARCHITECTURAL,
        pose=Pose.WEIGHT_SHIFT,
        body_angle=BodyAngle.THREE_QUARTER,
        camera_height=CameraHeight.CHEST,
        camera_distance=CameraDistance.MEDIUM_FULL,
        subject_position=SubjectPosition.LEFT_THIRD,
        outfit_frame_occupancy=70,
        negative_space=NegativeSpace.ENVIRONMENTAL,
        background_texture=BackgroundTexture.GLASS_METAL,
        background_clarity=BackgroundClarity.CRISP,
        lighting=Lighting.OVERCAST_DAYLIGHT,
        editorial_mood=EditorialMood.SUBDUED,
    ),
    ArtDirectionPreset.CANDID_URBAN: ArtDirection(
        preset=ArtDirectionPreset.CANDID_URBAN,
        pose=Pose.STEP_FORWARD,
        body_angle=BodyAngle.THREE_QUARTER,
        camera_height=CameraHeight.WAIST,
        camera_distance=CameraDistance.MEDIUM_FULL,
        subject_position=SubjectPosition.RIGHT_THIRD,
        outfit_frame_occupancy=76,
        negative_space=NegativeSpace.RIGHT,
        background_texture=BackgroundTexture.BRICK,
        background_clarity=BackgroundClarity.MODERATE,
        lighting=Lighting.AVAILABLE_LIGHT,
        editorial_mood=EditorialMood.CANDID,
    ),
    ArtDirectionPreset.LOW_ANGLE_EDITORIAL: ArtDirection(
        preset=ArtDirectionPreset.LOW_ANGLE_EDITORIAL,
        pose=Pose.ADJUSTING_OUTER,
        body_angle=BodyAngle.THREE_QUARTER,
        camera_height=CameraHeight.SLIGHT_LOW,
        camera_distance=CameraDistance.MEDIUM_FULL,
        subject_position=SubjectPosition.LEFT_THIRD,
        outfit_frame_occupancy=78,
        negative_space=NegativeSpace.UPPER,
        background_texture=BackgroundTexture.CONCRETE,
        background_clarity=BackgroundClarity.MODERATE,
        lighting=Lighting.AVAILABLE_LIGHT,
        editorial_mood=EditorialMood.RAW,
    ),
    ArtDirectionPreset.TEXTURED_STREET: ArtDirection(
        preset=ArtDirectionPreset.TEXTURED_STREET,
        pose=Pose.TURNED_TORSO,
        body_angle=BodyAngle.THREE_QUARTER,
        camera_height=CameraHeight.WAIST,
        camera_distance=CameraDistance.MEDIUM_FULL,
        subject_position=SubjectPosition.RIGHT_THIRD,
        outfit_frame_occupancy=74,
        negative_space=NegativeSpace.ENVIRONMENTAL,
        background_texture=BackgroundTexture.TEXTURED_WALL,
        background_clarity=BackgroundClarity.CRISP,
        lighting=Lighting.SOFT_DAYLIGHT,
        editorial_mood=EditorialMood.QUIET,
    ),
}

STYLE_ART_DIRECTION_PREFERENCES: dict[StylePreset, tuple[ArtDirectionPreset, ...]] = {
    StylePreset.SOFT_BOYFRIEND: (
        ArtDirectionPreset.PINTEREST_STREET,
        ArtDirectionPreset.CANDID_URBAN,
        ArtDirectionPreset.CLEAN_ARCHITECTURAL,
    ),
    StylePreset.MINIMAL: (
        ArtDirectionPreset.CLEAN_ARCHITECTURAL,
        ArtDirectionPreset.PINTEREST_STREET,
        ArtDirectionPreset.LOW_ANGLE_EDITORIAL,
    ),
    StylePreset.AMEKAJI: (
        ArtDirectionPreset.TEXTURED_STREET,
        ArtDirectionPreset.CANDID_URBAN,
        ArtDirectionPreset.PINTEREST_STREET,
    ),
    StylePreset.OTAKU_GRUNGE: (
        ArtDirectionPreset.TEXTURED_STREET,
        ArtDirectionPreset.LOW_ANGLE_EDITORIAL,
        ArtDirectionPreset.CANDID_URBAN,
        ArtDirectionPreset.PINTEREST_STREET,
    ),
}


def select_composition(
    style: StylePreset,
    target_date: date,
    recent_compositions: Iterable[CompositionPreset | str],
    *,
    allow_detail: bool = False,
) -> CompositionPreset:
    candidates = list(STYLE_COMPOSITION_PREFERENCES[style])
    if not allow_detail:
        candidates = [item for item in candidates if item is not CompositionPreset.DETAIL_EDITORIAL]
    return _select_non_repeating(
        candidates, target_date.toordinal(), _enum_set(recent_compositions)
    )


def select_scene(
    style: StylePreset,
    target_date: date,
    recent_scenes: Iterable[ScenePreset | str],
) -> ScenePreset:
    return _select_non_repeating(
        STYLE_SCENES[style], target_date.toordinal(), _enum_set(recent_scenes)
    )


def select_art_direction(
    style: StylePreset,
    target_date: date,
    recent_presets: Iterable[ArtDirectionPreset | str],
    composition: CompositionPreset,
) -> ArtDirection:
    preset = _select_non_repeating(
        STYLE_ART_DIRECTION_PREFERENCES[style],
        target_date.toordinal(),
        _enum_set(recent_presets),
    )
    direction = ART_DIRECTIONS[preset]
    if composition is CompositionPreset.REAR:
        return direction.model_copy(update={"body_angle": BodyAngle.REAR})
    if composition is CompositionPreset.THREE_QUARTER_REAR:
        return direction.model_copy(update={"body_angle": BodyAngle.THREE_QUARTER})
    if composition is CompositionPreset.DETAIL_EDITORIAL:
        return direction.model_copy(update={"camera_distance": CameraDistance.CLOSE_EDITORIAL})
    return direction


def _enum_set[T](values: Iterable[T | str]) -> set[T | str]:
    return set(values)


def _select_non_repeating[T](
    values: list[T] | tuple[T, ...], offset: int, recent: set[T | str]
) -> T:
    if not values:
        raise ValueError("at least one candidate is required")
    index = offset % len(values)
    rotated = [*values[index:], *values[:index]]
    for value in rotated:
        if value not in recent and value.value not in recent:
            return value
    return rotated[0]
