from __future__ import annotations

import json

from seoul_mens_daily_edit.images.domain import (
    ArtDirection,
    CompositionPreset,
    ImageGenerationPrompt,
    ReferenceImage,
    ScenePreset,
)
from seoul_mens_daily_edit.outfits.domain import OutfitRecipe
from seoul_mens_daily_edit.styling.domain import StylePreset, StyleSelection
from seoul_mens_daily_edit.weather.domain import WeatherSnapshot, get_styling_hints

FORBIDDEN_RECIPE_TERMS = (
    "brand",
    "product",
    "sku",
    "price",
    "shop",
    "purchase",
    "http://",
    "https://",
)

COMPOSITION_DIRECTIONS: dict[CompositionPreset, str] = {
    CompositionPreset.FACELESS_HERO: (
        "Vertical 4:5 men's fashion editorial photographed strictly from the base of the neck "
        "down to the shoes. The upper frame boundary intersects the subject at the base of the "
        "neck. Only the clothed body below the neck is inside the visible composition, with the "
        "complete outfit and shoes visible."
    ),
    CompositionPreset.EDITORIAL_CROP: (
        "Vertical 4:5 men's fashion editorial photographed strictly from the base of the neck "
        "down through the full outfit. The upper frame boundary intersects the subject at the "
        "base of the neck. Only the clothed body below the neck is inside the visible composition; "
        "the outfit is the visual subject."
    ),
    CompositionPreset.REAR: (
        "Complete rear-view fashion editorial. The subject faces fully away from the camera; the "
        "back of the head may remain in frame and the entire face remains invisible."
    ),
    CompositionPreset.THREE_QUARTER_REAR: (
        "Three-quarter rear fashion editorial. The subject's head, if in frame, is turned "
        "completely away from the camera so only the back of the head is visible and no facial "
        "profile is visible."
    ),
    CompositionPreset.STREET_SNAP: (
        "Candid street fashion frame. For any front, side, or three-quarter body angle, the entire "
        "head is completely outside the top edge of the frame and the upper boundary intersects at "
        "the base of the neck. A rear-facing subject may include only the back of the head; the "
        "entire face remains invisible."
    ),
    CompositionPreset.DETAIL_EDITORIAL: (
        "Close editorial detail that frames only garments, accessories, fabric, and footwear below "
        "the neck; no head or face region is included."
    ),
}


class ImagePromptBuilder:
    def build(
        self,
        weather_snapshot: WeatherSnapshot,
        style_selection: StyleSelection,
        outfit_recipe: OutfitRecipe,
        composition: CompositionPreset,
        *,
        scene: ScenePreset,
        art_direction: ArtDirection,
        reference_images: tuple[ReferenceImage, ...] = (),
    ) -> ImageGenerationPrompt:
        validate_image_context(weather_snapshot, style_selection, outfit_recipe)
        _validate_recipe_copy(outfit_recipe)
        hints = get_styling_hints(weather_snapshot)
        outfit_parts = _outfit_parts(outfit_recipe)
        palette = ", ".join(color.value.replace("_", " ") for color in outfit_recipe.palette)
        composition_direction = COMPOSITION_DIRECTIONS[composition]
        silhouette_direction = _silhouette_direction(outfit_recipe)
        garment_drape_direction = _garment_drape_direction(style_selection, outfit_recipe)
        style_direction = _style_direction(style_selection, outfit_recipe)
        art_direction_text = _art_direction_text(art_direction)
        reference_direction = (
            "Use the reference images only for visual grammar: silhouette, proportion, drape, "
            "camera framing, pose and editorial mood. Create a new original outfit. Do not "
            "reproduce the specific garments, graphics, logos or person."
        )
        prompt_sections = (
            composition_direction,
            f"Silhouette relationship: {silhouette_direction}.",
            f"Garment structure: {'; '.join(outfit_parts)}.",
            f"Garment drape: {garment_drape_direction}.",
            (
                "Proportion: "
                f"layering depth {outfit_recipe.layering_depth}; "
                f"top {outfit_recipe.top.fit.value}; bottom {outfit_recipe.bottom.fit.value}."
            ),
            f"Pose and art direction: {art_direction_text}.",
            f"Style grammar: {style_direction}.",
            f"Texture and palette: controlled {palette}; {_texture_direction(outfit_recipe)}.",
            f"Environment: {scene.value}; tactile background supports the outfit.",
            (
                "Camera: vertical 4:5 fashion editorial, realistic fabric texture and folds, "
                "realistic body proportions, and the shoes remain readable for hero frames."
            ),
            (
                "Weather context: Seoul tomorrow, "
                f"{weather_snapshot.weather_condition.value.replace('_', ' ')}, "
                f"high {weather_snapshot.high_temperature_c:g}C, "
                f"low {weather_snapshot.low_temperature_c:g}C, "
                f"precipitation probability {weather_snapshot.precipitation_probability:g}%, "
                f"temperature band {hints.temperature_band.value}."
            ),
            (
                "Use unbranded garments, original abstract graphics where applicable, clean "
                "unmarked textile surfaces, and a realistic wearable result."
            ),
            f"Art direction preset: {art_direction.preset.value}.",
        )
        text = "\n".join(
            (reference_direction, *prompt_sections) if reference_images else prompt_sections
        )
        return ImageGenerationPrompt(
            target_date=outfit_recipe.target_date,
            composition=composition,
            scene=scene,
            art_direction=art_direction,
            text=text,
            flux_structured_text=_build_flux_structured_text(
                composition_direction=composition_direction,
                silhouette_direction=silhouette_direction,
                scene=scene,
                outfit_parts=outfit_parts,
                palette=outfit_recipe.palette,
                style_direction=style_direction,
                art_direction=art_direction,
                reference_direction=reference_direction if reference_images else None,
                garment_drape_direction=garment_drape_direction,
            ),
            reference_images=reference_images,
        )


def validate_image_context(
    weather_snapshot: WeatherSnapshot,
    style_selection: StyleSelection,
    outfit_recipe: OutfitRecipe,
) -> None:
    if not isinstance(weather_snapshot, WeatherSnapshot):
        raise ValueError("weather_snapshot must be a WeatherSnapshot")
    if not isinstance(style_selection, StyleSelection):
        raise ValueError("style_selection must be a StyleSelection")
    if not isinstance(outfit_recipe, OutfitRecipe):
        raise ValueError("outfit_recipe must be an OutfitRecipe")
    if (
        len({weather_snapshot.target_date, style_selection.target_date, outfit_recipe.target_date})
        != 1
    ):
        raise ValueError(
            "weather_snapshot, style_selection, and outfit_recipe target_date must match"
        )
    if (
        outfit_recipe.style is not style_selection.style
        or outfit_recipe.occasion is not style_selection.occasion
        or outfit_recipe.mood is not style_selection.mood
    ):
        raise ValueError("outfit_recipe style context must match style_selection")


def _outfit_parts(recipe: OutfitRecipe) -> list[str]:
    parts = [
        f"{recipe.top.structure.value.replace('_', ' ')} top: {recipe.top.description}",
        f"{recipe.bottom.structure.value.replace('_', ' ')} lower: {recipe.bottom.description}",
        f"{recipe.shoes.shape.value.replace('_', ' ')} footwear: {recipe.shoes.description}",
    ]
    if recipe.outer is not None:
        parts.append(recipe.outer.description)
    if recipe.bag is not None:
        parts.append(recipe.bag.description)
    parts.extend(accessory.description for accessory in recipe.accessories)
    return parts


def _silhouette_direction(recipe: OutfitRecipe) -> str:
    silhouette = recipe.silhouette
    outer_length = (
        silhouette.outer_length.value.replace("_", " ") if silhouette.outer_length else "no"
    )
    return (
        f"{silhouette.strategy.value.replace('_', ' ')} strategy; "
        f"{silhouette.upper_volume.value} upper with {silhouette.top_length.value} top length and "
        f"{silhouette.shoulder_shape.value} shoulders; "
        f"{outer_length} outer length; {silhouette.lower_volume.value} lower; "
        f"{silhouette.pant_break.value.replace('_', ' ')} pant break; "
        f"{silhouette.footwear_weight.value} footwear visual weight"
    )


def _texture_direction(recipe: OutfitRecipe) -> str:
    profiles = ", ".join(profile.value.replace("_", " ") for profile in recipe.texture_profiles)
    if recipe.style is StylePreset.OTAKU_GRUNGE:
        return (
            f"{profiles}; washed, faded, matte, or distressed tonal separation keeps dark layers "
            "readable without accessory stacking"
        )
    if recipe.style is StylePreset.AMEKAJI:
        return "workwear texture and material contrast remain practical and everyday wearable"
    if recipe.style is StylePreset.SOFT_BOYFRIEND:
        return f"{profiles}; soft tactile texture and low contrast keep the drape approachable"
    return f"{profiles}; matte tonal separation and clean fabric edges keep visual noise restrained"


def _garment_drape_direction(style_selection: StyleSelection, recipe: OutfitRecipe) -> str:
    trouser_direction = (
        "trousers have a clean front rise, smooth uninterrupted drape from the waistband, "
        "sufficient ease through the upper trouser, controlled volume through the thigh, "
        "vertical fabric fall, and an intentional hem break"
    )
    if style_selection.style is StylePreset.SOFT_BOYFRIEND:
        return (
            "the regular-relaxed upper hangs with soft ease and the waist hardware stays quiet; "
            + trouser_direction
        )
    return trouser_direction


def _style_direction(style_selection: StyleSelection, recipe: OutfitRecipe) -> str:
    recipe_notes = " ".join(recipe.styling_notes)
    axis = recipe.content_axis.value.replace("_", " ") if recipe.content_axis else "none"
    return (
        f"{style_selection.style.value.replace('_', ' ').lower()}; "
        f"{style_selection.occasion.value.replace('_', ' ').lower()} occasion; "
        f"{style_selection.mood.value.lower()} mood; content axis {axis}. {recipe_notes}"
    )


def _art_direction_text(direction: ArtDirection) -> str:
    return (
        f"{direction.pose.value.replace('_', ' ')} pose, "
        f"{direction.body_angle.value.replace('_', ' ')} body angle, "
        f"{direction.camera_height.value.replace('_', ' ')} camera height, "
        f"{direction.camera_distance.value.replace('_', ' ')} distance, "
        f"subject at {direction.subject_position.value.replace('_', ' ')}, "
        f"outfit fills {direction.outfit_frame_occupancy}% of the frame, "
        f"{direction.negative_space.value} negative space, "
        f"{direction.background_clarity.value} "
        f"{direction.background_texture.value.replace('_', ' ')} "
        f"background, {direction.lighting.value.replace('_', ' ')} lighting, "
        f"{direction.editorial_mood.value} editorial mood"
    )


def _validate_recipe_copy(recipe: OutfitRecipe) -> None:
    recipe_copy = " ".join(
        (
            recipe.top.description,
            recipe.bottom.description,
            recipe.outer.description if recipe.outer is not None else "",
            recipe.shoes.description,
            recipe.bag.description if recipe.bag is not None else "",
            *(accessory.description for accessory in recipe.accessories),
            *recipe.styling_notes,
        )
    ).lower()
    if any(term in recipe_copy for term in FORBIDDEN_RECIPE_TERMS):
        raise ValueError("outfit_recipe contains prohibited commercial copy")


def _build_flux_structured_text(
    *,
    composition_direction: str,
    silhouette_direction: str,
    scene: ScenePreset,
    outfit_parts: list[str],
    palette: tuple[object, ...],
    style_direction: str,
    art_direction: ArtDirection,
    reference_direction: str | None,
    garment_drape_direction: str,
) -> str:
    """Serialize FLUX.2's documented JSON prompt shape for the Cloudflare adapter only."""
    document: dict[str, object] = {
        "composition": composition_direction,
        "silhouette": silhouette_direction,
        "garment_structure": "; ".join(outfit_parts),
        "garment_drape": garment_drape_direction,
        "proportions": silhouette_direction,
        "subjects": [
            {
                "description": "adult male fashion model; " + "; ".join(outfit_parts),
                "position": art_direction.subject_position.value.replace("_", " "),
                "action": art_direction.pose.value.replace("_", " "),
            }
        ],
        "style": style_direction,
        "color_palette": [str(color).replace("_", " ") for color in palette],
        "background": scene.value,
        "camera": {
            "orientation": "vertical 4:5",
            "height": art_direction.camera_height.value.replace("_", " "),
            "distance": art_direction.camera_distance.value.replace("_", " "),
            "body_angle": art_direction.body_angle.value.replace("_", " "),
            "outfit_frame_occupancy": art_direction.outfit_frame_occupancy,
            "negative_space": art_direction.negative_space.value,
        },
        "lighting": art_direction.lighting.value.replace("_", " "),
        "art_direction": art_direction.model_dump(mode="json"),
    }
    if reference_direction is not None:
        document = {"reference_use": reference_direction, **document}
    return json.dumps(document, ensure_ascii=False, separators=(",", ":"))
