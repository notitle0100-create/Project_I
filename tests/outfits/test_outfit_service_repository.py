from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from seoul_mens_daily_edit.db.base import Base
from seoul_mens_daily_edit.outfits.domain import OutfitRecipe
from seoul_mens_daily_edit.outfits.models import OutfitRecipeRecord
from seoul_mens_daily_edit.outfits.repository import OutfitRecipeRepository
from seoul_mens_daily_edit.outfits.service import generate_outfit_recipe
from seoul_mens_daily_edit.styling.domain import Mood, Occasion, StylePreset, StyleSelection
from seoul_mens_daily_edit.weather.domain import WeatherCondition, WeatherSnapshot


@pytest.fixture
def repository() -> OutfitRecipeRepository:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker[Session](bind=engine, expire_on_commit=False)
    yield OutfitRecipeRepository(session_factory)
    engine.dispose()


def make_weather_snapshot(target_date: date) -> WeatherSnapshot:
    return WeatherSnapshot(
        target_date=target_date,
        weather_condition=WeatherCondition.CLEAR,
        high_temperature_c=22,
        low_temperature_c=12,
        precipitation_probability=10,
        fetched_at=datetime(2026, 8, 19, 10, tzinfo=UTC),
    )


def make_selection(
    target_date: date, style: StylePreset = StylePreset.SOFT_BOYFRIEND
) -> StyleSelection:
    return StyleSelection(
        target_date=target_date,
        style=style,
        occasion=Occasion.DAILY,
        mood=Mood.CLEAN,
        selected_at=datetime(2026, 8, 19, 10, tzinfo=UTC),
    )


def test_recipe_is_persisted_and_same_target_date_is_idempotent(
    repository: OutfitRecipeRepository,
) -> None:
    target_date = date(2026, 8, 20)
    first = generate_outfit_recipe(
        make_weather_snapshot(target_date), make_selection(target_date), repository
    )
    repeated = generate_outfit_recipe(
        make_weather_snapshot(target_date),
        make_selection(target_date, StylePreset.MINIMAL),
        repository,
    )
    with repository._session_factory() as session:
        count = session.scalar(select(func.count()).select_from(OutfitRecipeRecord))

    assert repeated == first
    assert count == 1


def test_recent_persisted_recipe_reduces_duplicate_signature(
    repository: OutfitRecipeRepository,
) -> None:
    first_date = date(2026, 8, 20)
    first = generate_outfit_recipe(
        make_weather_snapshot(first_date), make_selection(first_date), repository
    )
    second_date = first_date + timedelta(days=2)
    second = generate_outfit_recipe(
        make_weather_snapshot(second_date), make_selection(second_date), repository
    )

    assert second.signature != first.signature


def test_service_rejects_missing_or_mismatched_inputs(repository: OutfitRecipeRepository) -> None:
    target_date = date(2026, 8, 20)

    with pytest.raises(ValueError, match="weather_snapshot"):
        generate_outfit_recipe(None, make_selection(target_date), repository)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="target_date"):
        generate_outfit_recipe(
            make_weather_snapshot(target_date),
            make_selection(target_date + timedelta(days=1)),
            repository,
        )


def test_recipe_schema_rejects_malformed_palette() -> None:
    with pytest.raises(ValidationError, match="palette colors must be unique"):
        OutfitRecipe.model_validate(
            {
                "target_date": "2026-08-20",
                "style": "MINIMAL",
                "occasion": "DAILY",
                "mood": "CLEAN",
                "top": {
                    "category": "tee",
                    "fit": "regular",
                    "color": "black",
                    "description": "plain tee",
                },
                "bottom": {
                    "category": "trousers",
                    "fit": "straight",
                    "color": "black",
                    "description": "plain trousers",
                },
                "outer": None,
                "shoes": {
                    "category": "sneakers",
                    "color": "black",
                    "description": "plain sneakers",
                },
                "bag": None,
                "accessories": [],
                "palette": ["black", "black"],
                "layering_depth": 1,
                "styling_notes": ["Keep it clean."],
            }
        )
