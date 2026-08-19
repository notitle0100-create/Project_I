from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, model_validator


class StylePreset(StrEnum):
    SOFT_BOYFRIEND = "SOFT_BOYFRIEND"
    MINIMAL = "MINIMAL"
    AMEKAJI = "AMEKAJI"
    OTAKU_GRUNGE = "OTAKU_GRUNGE"


class Occasion(StrEnum):
    DAILY = "DAILY"
    UNIVERSITY = "UNIVERSITY"
    DATE = "DATE"
    CAFE = "CAFE"
    WEEKEND = "WEEKEND"
    LIGHT_WORK = "LIGHT_WORK"
    EXHIBITION = "EXHIBITION"
    TRAVEL = "TRAVEL"
    NEIGHBORHOOD = "NEIGHBORHOOD"


class Mood(StrEnum):
    CLEAN = "CLEAN"
    RELAXED = "RELAXED"
    SOFT = "SOFT"
    URBAN = "URBAN"
    VINTAGE = "VINTAGE"
    RUGGED = "RUGGED"
    DARK = "DARK"
    EXPERIMENTAL = "EXPERIMENTAL"


class StyleSelection(BaseModel):
    model_config = ConfigDict(frozen=True)

    target_date: date
    style: StylePreset
    occasion: Occasion
    mood: Mood
    selected_at: datetime

    @model_validator(mode="after")
    def validate_selected_at(self) -> StyleSelection:
        if self.selected_at.tzinfo is None or self.selected_at.utcoffset() is None:
            raise ValueError("selected_at must be timezone-aware")
        return self
