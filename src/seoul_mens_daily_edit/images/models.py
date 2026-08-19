from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from seoul_mens_daily_edit.db.base import Base


class ImageGenerationRecord(Base):
    __tablename__ = "image_generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_date: Mapped[date] = mapped_column(Date, unique=True)
    recipe_target_date: Mapped[date] = mapped_column(Date)
    model: Mapped[str] = mapped_column(String(128))
    prompt: Mapped[str] = mapped_column(Text)
    composition: Mapped[str] = mapped_column(String(32))
    scene: Mapped[str] = mapped_column(String(160))
    generation_size: Mapped[str] = mapped_column(String(16))
    final_width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    final_height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(16))
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
