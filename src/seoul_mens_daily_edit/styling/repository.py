from __future__ import annotations

from datetime import UTC, date

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from seoul_mens_daily_edit.styling.domain import Mood, Occasion, StylePreset, StyleSelection
from seoul_mens_daily_edit.styling.models import StyleSelectionRecord


class StyleSelectionRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get_by_target_date(self, target_date: date) -> StyleSelection | None:
        with self._session_factory() as session:
            record = session.scalar(
                select(StyleSelectionRecord).where(StyleSelectionRecord.target_date == target_date)
            )
            return _to_selection(record) if record is not None else None

    def get_recent(self, limit: int) -> list[StyleSelection]:
        if limit < 1:
            raise ValueError("limit must be positive")
        with self._session_factory() as session:
            records = session.scalars(
                select(StyleSelectionRecord)
                .order_by(StyleSelectionRecord.selected_at.desc(), StyleSelectionRecord.id.desc())
                .limit(limit)
            )
            return [_to_selection(record) for record in records]

    def count(self) -> int:
        with self._session_factory() as session:
            return int(session.scalar(select(func.count()).select_from(StyleSelectionRecord)) or 0)

    def get_or_create(self, candidate: StyleSelection) -> StyleSelection:
        existing = self.get_by_target_date(candidate.target_date)
        if existing is not None:
            return existing

        try:
            with self._session_factory() as session:
                session.add(_to_record(candidate))
                session.commit()
            return candidate
        except IntegrityError:
            existing = self.get_by_target_date(candidate.target_date)
            if existing is None:
                raise
            return existing


def _to_record(selection: StyleSelection) -> StyleSelectionRecord:
    return StyleSelectionRecord(
        target_date=selection.target_date,
        style=selection.style.value,
        occasion=selection.occasion.value,
        mood=selection.mood.value,
        selected_at=selection.selected_at,
    )


def _to_selection(record: StyleSelectionRecord) -> StyleSelection:
    selected_at = record.selected_at
    if selected_at.tzinfo is None or selected_at.utcoffset() is None:
        selected_at = selected_at.replace(tzinfo=UTC)
    return StyleSelection(
        target_date=record.target_date,
        style=StylePreset(record.style),
        occasion=Occasion(record.occasion),
        mood=Mood(record.mood),
        selected_at=selected_at,
    )
