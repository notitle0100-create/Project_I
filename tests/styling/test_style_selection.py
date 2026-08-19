from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from seoul_mens_daily_edit.db.base import Base
from seoul_mens_daily_edit.styling.domain import Mood, Occasion, StylePreset, StyleSelection
from seoul_mens_daily_edit.styling.models import StyleSelectionRecord
from seoul_mens_daily_edit.styling.repository import StyleSelectionRepository
from seoul_mens_daily_edit.styling.service import select_style_context
from seoul_mens_daily_edit.weather.domain import WeatherCondition, WeatherSnapshot


@pytest.fixture
def repository() -> StyleSelectionRepository:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker[Session](bind=engine, expire_on_commit=False)
    yield StyleSelectionRepository(session_factory)
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


def select_for_date(repository: StyleSelectionRepository, target_date: date) -> StyleSelection:
    return select_style_context(
        target_date,
        make_weather_snapshot(target_date),
        repository,
        selected_at=datetime(2026, 8, 19, 10, tzinfo=UTC),
    )


def test_rotation_order_and_wraparound(repository: StyleSelectionRepository) -> None:
    start = date(2026, 8, 20)

    selections = [select_for_date(repository, start + timedelta(days=index)) for index in range(5)]

    assert [selection.style for selection in selections] == [
        StylePreset.SOFT_BOYFRIEND,
        StylePreset.MINIMAL,
        StylePreset.AMEKAJI,
        StylePreset.OTAKU_GRUNGE,
        StylePreset.SOFT_BOYFRIEND,
    ]


def test_restart_uses_persisted_history_for_next_rotation(
    repository: StyleSelectionRepository,
) -> None:
    start = date(2026, 8, 20)
    for index in range(3):
        select_for_date(repository, start + timedelta(days=index))

    restarted_repository = StyleSelectionRepository(repository._session_factory)
    selection = select_for_date(restarted_repository, start + timedelta(days=3))

    assert selection.style is StylePreset.OTAKU_GRUNGE


def test_same_target_date_is_idempotent_and_does_not_advance_rotation(
    repository: StyleSelectionRepository,
) -> None:
    target_date = date(2026, 8, 20)

    first = select_for_date(repository, target_date)
    repeated = select_for_date(repository, target_date)
    next_selection = select_for_date(repository, target_date + timedelta(days=1))

    assert repeated == first
    assert next_selection.style is StylePreset.MINIMAL


def test_persistence_keeps_one_row_for_duplicate_candidate(
    repository: StyleSelectionRepository,
) -> None:
    first = StyleSelection(
        target_date=date(2026, 8, 20),
        style=StylePreset.SOFT_BOYFRIEND,
        occasion=Occasion.DAILY,
        mood=Mood.CLEAN,
        selected_at=datetime(2026, 8, 19, 10, tzinfo=UTC),
    )
    duplicate = first.model_copy(update={"style": StylePreset.MINIMAL})

    persisted = repository.get_or_create(first)
    duplicate_result = repository.get_or_create(duplicate)
    with repository._session_factory() as session:
        count = session.scalar(select(func.count()).select_from(StyleSelectionRecord))

    assert duplicate_result == persisted
    assert count == 1


def test_selection_returns_controlled_occasion_and_mood(
    repository: StyleSelectionRepository,
) -> None:
    selection = select_for_date(repository, date(2026, 8, 20))

    assert selection.occasion in Occasion
    assert selection.mood in Mood


def test_selection_rejects_missing_or_mismatched_weather_snapshot(
    repository: StyleSelectionRepository,
) -> None:
    target_date = date(2026, 8, 20)

    with pytest.raises(ValueError, match="weather_snapshot"):
        select_style_context(target_date, None, repository)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="target_date"):
        select_style_context(
            target_date,
            make_weather_snapshot(target_date + timedelta(days=1)),
            repository,
        )


def test_selection_rejects_datetime_target_date(repository: StyleSelectionRepository) -> None:
    target_datetime = datetime(2026, 8, 20, tzinfo=UTC)

    with pytest.raises(ValueError, match="date, not a datetime"):
        select_style_context(
            target_datetime,
            make_weather_snapshot(target_datetime.date()),
            repository,
        )
