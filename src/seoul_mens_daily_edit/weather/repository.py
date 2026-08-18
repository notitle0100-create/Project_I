from __future__ import annotations

from datetime import UTC, date

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from seoul_mens_daily_edit.weather.domain import WeatherCondition, WeatherSnapshot
from seoul_mens_daily_edit.weather.models import WeatherSnapshotRecord


class WeatherSnapshotRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def save(self, snapshot: WeatherSnapshot) -> WeatherSnapshot:
        with self._session_factory() as session:
            record = session.scalar(
                select(WeatherSnapshotRecord).where(
                    WeatherSnapshotRecord.target_date == snapshot.target_date
                )
            )
            if record is None:
                record = WeatherSnapshotRecord(target_date=snapshot.target_date)
                session.add(record)

            record.timezone = snapshot.timezone
            record.weather_condition = snapshot.weather_condition.value
            record.high_temperature_c = snapshot.high_temperature_c
            record.low_temperature_c = snapshot.low_temperature_c
            record.precipitation_probability = snapshot.precipitation_probability
            record.fetched_at = snapshot.fetched_at
            session.commit()

        return snapshot

    def get_by_target_date(self, target_date: date) -> WeatherSnapshot | None:
        with self._session_factory() as session:
            record = session.scalar(
                select(WeatherSnapshotRecord).where(
                    WeatherSnapshotRecord.target_date == target_date
                )
            )
            return _to_snapshot(record) if record is not None else None


def _to_snapshot(record: WeatherSnapshotRecord) -> WeatherSnapshot:
    fetched_at = record.fetched_at
    if fetched_at.tzinfo is None or fetched_at.utcoffset() is None:
        fetched_at = fetched_at.replace(tzinfo=UTC)
    return WeatherSnapshot(
        target_date=record.target_date,
        timezone=record.timezone,
        weather_condition=WeatherCondition(record.weather_condition),
        high_temperature_c=record.high_temperature_c,
        low_temperature_c=record.low_temperature_c,
        precipitation_probability=record.precipitation_probability,
        fetched_at=fetched_at,
    )
