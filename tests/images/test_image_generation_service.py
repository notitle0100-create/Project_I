from __future__ import annotations

import base64
from datetime import UTC, date, datetime
from io import BytesIO

import pytest
from PIL import Image
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from seoul_mens_daily_edit.db.base import Base
from seoul_mens_daily_edit.images.domain import (
    GeneratedImagePayload,
    ImageGenerationPrompt,
    ImageGenerationStatus,
)
from seoul_mens_daily_edit.images.models import ImageGenerationRecord
from seoul_mens_daily_edit.images.processor import ImageProcessor
from seoul_mens_daily_edit.images.prompt_builder import ImagePromptBuilder
from seoul_mens_daily_edit.images.provider import ImageProviderError
from seoul_mens_daily_edit.images.repository import ImageGenerationRepository
from seoul_mens_daily_edit.images.service import ImageGenerationError, ImageGenerationService
from seoul_mens_daily_edit.outfits.policy import build_recipe_candidates
from seoul_mens_daily_edit.styling.domain import Mood, Occasion, StylePreset, StyleSelection
from seoul_mens_daily_edit.weather.domain import WeatherCondition, WeatherSnapshot


@pytest.fixture
def repository() -> ImageGenerationRepository:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker[Session](bind=engine, expire_on_commit=False)
    yield ImageGenerationRepository(session_factory)
    engine.dispose()


class FakeProvider:
    def __init__(
        self, encoded_image: str | None = None, error: ImageProviderError | None = None
    ) -> None:
        self._encoded_image = encoded_image
        self._error = error
        self.calls = 0

    def generate(
        self, prompt: ImageGenerationPrompt, width: int, height: int
    ) -> GeneratedImagePayload:
        self.calls += 1
        assert prompt.flux_structured_text is not None
        assert (width, height) == (1088, 1360)
        if self._error is not None:
            raise self._error
        assert self._encoded_image is not None
        return GeneratedImagePayload(image_base64=self._encoded_image)


def make_weather_snapshot(target_date: date) -> WeatherSnapshot:
    return WeatherSnapshot(
        target_date=target_date,
        weather_condition=WeatherCondition.CLEAR,
        high_temperature_c=22,
        low_temperature_c=12,
        precipitation_probability=10,
        fetched_at=datetime(2026, 8, 19, 10, tzinfo=UTC),
    )


def make_selection(target_date: date) -> StyleSelection:
    return StyleSelection(
        target_date=target_date,
        style=StylePreset.OTAKU_GRUNGE,
        occasion=Occasion.DAILY,
        mood=Mood.DARK,
        selected_at=datetime(2026, 8, 19, 10, tzinfo=UTC),
    )


def make_service(
    repository: ImageGenerationRepository,
    provider: FakeProvider,
    tmp_path,
) -> ImageGenerationService:
    return ImageGenerationService(
        repository,
        ImagePromptBuilder(),
        provider,
        ImageProcessor(tmp_path, "1088x1360"),
        model="gpt-image-2",
        generation_size="1088x1360",
    )


def test_generation_persists_metadata_and_is_idempotent(
    repository: ImageGenerationRepository,
    tmp_path,
) -> None:
    target_date = date(2026, 8, 20)
    weather = make_weather_snapshot(target_date)
    selection = make_selection(target_date)
    recipe = build_recipe_candidates(weather, selection)[0]
    provider = FakeProvider(make_encoded_png((1088, 1360)))
    service = make_service(repository, provider, tmp_path)

    first = service.generate(weather, selection, recipe)
    repeated = service.generate(weather, selection, recipe)
    with repository._session_factory() as session:
        count = session.scalar(select(func.count()).select_from(ImageGenerationRecord))

    assert first.status is ImageGenerationStatus.GENERATED
    assert first.file_path is not None
    assert (first.final_width, first.final_height) == (1080, 1350)
    assert repeated == first
    assert provider.calls == 1
    assert count == 1
    assert len(repository.get_recent_art_direction_presets(1)) == 1


def test_provider_failure_is_persisted_without_raw_error_details(
    repository: ImageGenerationRepository,
    tmp_path,
) -> None:
    target_date = date(2026, 8, 20)
    weather = make_weather_snapshot(target_date)
    selection = make_selection(target_date)
    recipe = build_recipe_candidates(weather, selection)[0]
    provider = FakeProvider(error=ImageProviderError("provider_authentication", retryable=False))
    service = make_service(repository, provider, tmp_path)

    with pytest.raises(ImageGenerationError, match="provider_authentication"):
        service.generate(weather, selection, recipe)
    stored = repository.get_by_target_date(target_date)

    assert stored is not None
    assert stored.status is ImageGenerationStatus.FAILED
    assert stored.error_code == "provider_authentication"
    assert "key" not in (stored.error_code or "").lower()


def test_corrupt_provider_image_is_marked_failed(
    repository: ImageGenerationRepository,
    tmp_path,
) -> None:
    target_date = date(2026, 8, 20)
    weather = make_weather_snapshot(target_date)
    selection = make_selection(target_date)
    recipe = build_recipe_candidates(weather, selection)[0]
    service = make_service(repository, FakeProvider("not-base64"), tmp_path)

    with pytest.raises(ImageGenerationError, match="invalid_image"):
        service.generate(weather, selection, recipe)

    assert repository.get_by_target_date(target_date).status is ImageGenerationStatus.FAILED  # type: ignore[union-attr]


def test_invalid_context_is_rejected_before_a_generation_record_is_created(
    repository: ImageGenerationRepository,
    tmp_path,
) -> None:
    target_date = date(2026, 8, 20)
    weather = make_weather_snapshot(target_date)
    recipe = build_recipe_candidates(weather, make_selection(target_date))[0]
    service = make_service(
        repository,
        FakeProvider(make_encoded_png((1088, 1360))),
        tmp_path,
    )

    with pytest.raises(ValueError, match="target_date must match"):
        service.generate(weather, make_selection(date(2026, 8, 21)), recipe)

    assert repository.get_by_target_date(target_date) is None


def make_encoded_png(size: tuple[int, int]) -> str:
    buffer = BytesIO()
    Image.new("RGB", size, color="black").save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")
