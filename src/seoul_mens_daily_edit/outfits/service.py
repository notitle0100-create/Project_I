from __future__ import annotations

from seoul_mens_daily_edit.outfits.domain import OutfitRecipe
from seoul_mens_daily_edit.outfits.policy import (
    RECENT_RECIPE_LIMIT,
    build_recipe_candidates,
    select_recipe_candidate,
)
from seoul_mens_daily_edit.outfits.repository import OutfitRecipeRepository
from seoul_mens_daily_edit.styling.domain import StyleSelection
from seoul_mens_daily_edit.weather.domain import WeatherSnapshot


def generate_outfit_recipe(
    weather_snapshot: WeatherSnapshot,
    style_selection: StyleSelection,
    repository: OutfitRecipeRepository,
) -> OutfitRecipe:
    if not isinstance(weather_snapshot, WeatherSnapshot):
        raise ValueError("weather_snapshot must be a WeatherSnapshot")
    if not isinstance(style_selection, StyleSelection):
        raise ValueError("style_selection must be a StyleSelection")
    if weather_snapshot.target_date != style_selection.target_date:
        raise ValueError("weather_snapshot and style_selection target_date must match")

    existing = repository.get_by_target_date(weather_snapshot.target_date)
    if existing is not None:
        return existing

    candidates = build_recipe_candidates(weather_snapshot, style_selection)
    recent_recipes = repository.get_recent(RECENT_RECIPE_LIMIT)
    candidate = select_recipe_candidate(
        candidates,
        {recipe.signature for recipe in recent_recipes},
        weather_snapshot,
    )
    return repository.get_or_create(candidate)
