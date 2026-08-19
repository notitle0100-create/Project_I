from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from seoul_mens_daily_edit.images.domain import (
    GeneratedImage,
    ImageGenerationPrompt,
    ImageGenerationStatus,
)
from seoul_mens_daily_edit.images.models import ImageGenerationRecord
from seoul_mens_daily_edit.images.processor import ProcessedImage


class ImageGenerationRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get_by_target_date(self, target_date: date) -> GeneratedImage | None:
        with self._session_factory() as session:
            record = session.scalar(
                select(ImageGenerationRecord).where(
                    ImageGenerationRecord.target_date == target_date
                )
            )
            return _to_generated_image(record) if record is not None else None

    def get_recent_compositions(self, limit: int) -> list[str]:
        return [record.composition for record in self._recent_successes(limit)]

    def get_recent_scenes(self, limit: int) -> list[str]:
        return [record.scene for record in self._recent_successes(limit)]

    def begin(
        self,
        prompt: ImageGenerationPrompt,
        *,
        model: str,
        generation_size: str,
        started_at: datetime | None = None,
    ) -> GeneratedImage:
        now = started_at or datetime.now(UTC)
        try:
            with self._session_factory() as session:
                record = session.scalar(
                    select(ImageGenerationRecord).where(
                        ImageGenerationRecord.target_date == prompt.target_date
                    )
                )
                if record is None:
                    record = ImageGenerationRecord(
                        target_date=prompt.target_date,
                        recipe_target_date=prompt.target_date,
                        model=model,
                        prompt=prompt.text,
                        composition=prompt.composition.value,
                        scene=prompt.scene,
                        generation_size=generation_size,
                        final_width=None,
                        final_height=None,
                        file_path=None,
                        status=ImageGenerationStatus.PENDING.value,
                        error_code=None,
                        created_at=now,
                        updated_at=now,
                    )
                    session.add(record)
                    session.flush()
                record.model = model
                record.prompt = prompt.text
                record.composition = prompt.composition.value
                record.scene = prompt.scene
                record.generation_size = generation_size
                record.final_width = None
                record.final_height = None
                record.file_path = None
                record.status = ImageGenerationStatus.GENERATING.value
                record.error_code = None
                record.updated_at = now
                session.commit()
                session.refresh(record)
                return _to_generated_image(record)
        except IntegrityError:
            existing = self.get_by_target_date(prompt.target_date)
            if existing is None:
                raise
            return existing

    def mark_generated(
        self,
        generation_id: int,
        processed_image: ProcessedImage,
        *,
        updated_at: datetime | None = None,
    ) -> GeneratedImage:
        return self._finish(
            generation_id,
            status=ImageGenerationStatus.GENERATED,
            processed_image=processed_image,
            error_code=None,
            updated_at=updated_at,
        )

    def mark_failed(
        self,
        generation_id: int,
        error_code: str,
        *,
        updated_at: datetime | None = None,
    ) -> GeneratedImage:
        return self._finish(
            generation_id,
            status=ImageGenerationStatus.FAILED,
            processed_image=None,
            error_code=error_code,
            updated_at=updated_at,
        )

    def _recent_successes(self, limit: int) -> list[ImageGenerationRecord]:
        if limit < 1:
            raise ValueError("limit must be positive")
        with self._session_factory() as session:
            return list(
                session.scalars(
                    select(ImageGenerationRecord)
                    .where(ImageGenerationRecord.status == ImageGenerationStatus.GENERATED.value)
                    .order_by(
                        ImageGenerationRecord.created_at.desc(), ImageGenerationRecord.id.desc()
                    )
                    .limit(limit)
                )
            )

    def _finish(
        self,
        generation_id: int,
        *,
        status: ImageGenerationStatus,
        processed_image: ProcessedImage | None,
        error_code: str | None,
        updated_at: datetime | None,
    ) -> GeneratedImage:
        with self._session_factory() as session:
            record = session.get(ImageGenerationRecord, generation_id)
            if record is None:
                raise ValueError("image generation record does not exist")
            record.status = status.value
            record.error_code = error_code
            record.updated_at = updated_at or datetime.now(UTC)
            if processed_image is not None:
                record.file_path = processed_image.file_path
                record.final_width = processed_image.width
                record.final_height = processed_image.height
            session.commit()
            session.refresh(record)
            return _to_generated_image(record)


def _to_generated_image(record: ImageGenerationRecord) -> GeneratedImage:
    return GeneratedImage(
        id=record.id,
        target_date=record.target_date,
        recipe_target_date=record.recipe_target_date,
        model=record.model,
        prompt=record.prompt,
        composition=record.composition,
        scene=record.scene,
        generation_size=record.generation_size,
        final_width=record.final_width,
        final_height=record.final_height,
        file_path=record.file_path,
        status=record.status,
        error_code=record.error_code,
        created_at=_aware_datetime(record.created_at),
        updated_at=_aware_datetime(record.updated_at),
    )


def _aware_datetime(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=UTC)
    return value
