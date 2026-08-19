from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from seoul_mens_daily_edit.outfits.domain import OutfitRecipe
from seoul_mens_daily_edit.outfits.models import OutfitRecipeRecord


class OutfitRecipeRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get_by_target_date(self, target_date: date) -> OutfitRecipe | None:
        with self._session_factory() as session:
            record = session.scalar(
                select(OutfitRecipeRecord).where(OutfitRecipeRecord.target_date == target_date)
            )
            return _to_recipe(record) if record is not None else None

    def get_recent(self, limit: int) -> list[OutfitRecipe]:
        if limit < 1:
            raise ValueError("limit must be positive")
        with self._session_factory() as session:
            records = session.scalars(
                select(OutfitRecipeRecord)
                .order_by(OutfitRecipeRecord.created_at.desc(), OutfitRecipeRecord.id.desc())
                .limit(limit)
            )
            return [_to_recipe(record) for record in records]

    def get_or_create(
        self, candidate: OutfitRecipe, *, created_at: datetime | None = None
    ) -> OutfitRecipe:
        existing = self.get_by_target_date(candidate.target_date)
        if existing is not None:
            return existing
        try:
            with self._session_factory() as session:
                session.add(
                    OutfitRecipeRecord(
                        target_date=candidate.target_date,
                        recipe=candidate.model_dump(mode="json"),
                        created_at=created_at or datetime.now(UTC),
                    )
                )
                session.commit()
            return candidate
        except IntegrityError:
            existing = self.get_by_target_date(candidate.target_date)
            if existing is None:
                raise
            return existing


def _to_recipe(record: OutfitRecipeRecord) -> OutfitRecipe:
    return OutfitRecipe.model_validate(record.recipe)
