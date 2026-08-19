from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from seoul_mens_daily_edit.db.base import Base


class StyleSelectionRecord(Base):
    __tablename__ = "style_selections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_date: Mapped[date] = mapped_column(Date, unique=True)
    style: Mapped[str] = mapped_column(String(32))
    occasion: Mapped[str] = mapped_column(String(32))
    mood: Mapped[str] = mapped_column(String(32))
    selected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
