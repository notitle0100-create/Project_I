from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import JSON, Date, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from seoul_mens_daily_edit.db.base import Base


class OutfitRecipeRecord(Base):
    __tablename__ = "outfit_recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_date: Mapped[date] = mapped_column(Date, unique=True)
    recipe: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
