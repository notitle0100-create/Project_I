from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from seoul_mens_daily_edit.db.base import Base


class WeatherSnapshotRecord(Base):
    __tablename__ = "weather_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_date: Mapped[date] = mapped_column(Date, unique=True)
    timezone: Mapped[str] = mapped_column(String(64))
    weather_condition: Mapped[str] = mapped_column(String(32))
    high_temperature_c: Mapped[float] = mapped_column(Float)
    low_temperature_c: Mapped[float] = mapped_column(Float)
    precipitation_probability: Mapped[float] = mapped_column(Float)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
