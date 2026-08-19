from __future__ import annotations

from seoul_mens_daily_edit.images.domain import CompositionPreset, ImageGenerationPrompt
from seoul_mens_daily_edit.outfits.domain import OutfitRecipe
from seoul_mens_daily_edit.styling.domain import StyleSelection
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
    CompositionPreset.FACELESS_HERO: "full outfit editorial, head naturally outside the frame",
    CompositionPreset.EDITORIAL_CROP: "editorial crop that excludes every facial feature",
    CompositionPreset.REAR: "complete rear view with the face fully turned away",
    CompositionPreset.THREE_QUARTER_REAR: "three-quarter rear view with no face visible",
    CompositionPreset.STREET_SNAP: (
        "candid street fashion frame with the face outside the composition"
    ),
    CompositionPreset.DETAIL_EDITORIAL: (
        "close editorial detail of the outfit, no head or facial features in frame"
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
        scene: str,
    ) -> ImageGenerationPrompt:
        validate_image_context(weather_snapshot, style_selection, outfit_recipe)
        _validate_recipe_copy(outfit_recipe)
        hints = get_styling_hints(weather_snapshot)
        outfit_parts = [
            outfit_recipe.top.description,
            outfit_recipe.bottom.description,
            outfit_recipe.shoes.description,
        ]
        if outfit_recipe.outer is not None:
            outfit_parts.append(outfit_recipe.outer.description)
        if outfit_recipe.bag is not None:
            outfit_parts.append(outfit_recipe.bag.description)
        outfit_parts.extend(accessory.description for accessory in outfit_recipe.accessories)
        palette = ", ".join(color.value.replace("_", " ") for color in outfit_recipe.palette)
        text = "\n".join(
            (
                (
                    "A. SUBJECT: slim-to-average adult male fashion model silhouette; "
                    "no specific person."
                ),
                f"B. OUTFIT: {'; '.join(outfit_parts)}.",
                (
                    "C. SILHOUETTE / FIT: "
                    f"top {outfit_recipe.top.fit.value}, bottom {outfit_recipe.bottom.fit.value}, "
                    f"layering depth {outfit_recipe.layering_depth}."
                ),
                f"D. COLOR PALETTE: controlled {palette} palette.",
                (
                    "E. WEATHER CONTEXT: Seoul tomorrow, "
                    f"{weather_snapshot.weather_condition.value.replace('_', ' ')}, "
                    f"high {weather_snapshot.high_temperature_c:g}C, "
                    f"low {weather_snapshot.low_temperature_c:g}C, "
                    f"precipitation probability {weather_snapshot.precipitation_probability:g}%, "
                    f"temperature band {hints.temperature_band.value}."
                ),
                (
                    "F. STYLE / MOOD: "
                    f"{style_selection.style.value.replace('_', ' ').lower()}, "
                    f"{style_selection.occasion.value.replace('_', ' ').lower()}, "
                    f"{style_selection.mood.value.lower()}."
                ),
                f"G. COMPOSITION: {COMPOSITION_DIRECTIONS[composition]}.",
                f"H. ENVIRONMENT: {scene}; background remains secondary to the outfit.",
                (
                    "I. PHOTOGRAPHY / EDITORIAL DIRECTION: photorealistic premium contemporary "
                    "fashion magazine, natural lighting, realistic fabric texture and folds, "
                    "realistic body proportions, subtle depth of field, clean composition, "
                    "understated editorial color grading."
                ),
                (
                    "J. FACELESS HARD CONSTRAINTS: never show a recognizable face, eyes, eyebrows, "
                    "nose, mouth, cheeks, chin, or jawline. Hair and the back of the head "
                    "may be visible."
                ),
                (
                    "K. NEGATIVE / AVOID CONSTRAINTS: no cosplay, costume styling, copyrighted "
                    "character reproduction, real brand logos, random text, watermark, "
                    "price labels, plastic skin, malformed hands or legs, deformed shoes, "
                    "fused clothing or body, "
                    "impossible fabric, duplicated accessories, or floating objects."
                ),
            )
        )
        return ImageGenerationPrompt(
            target_date=outfit_recipe.target_date,
            composition=composition,
            scene=scene,
            text=text,
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
