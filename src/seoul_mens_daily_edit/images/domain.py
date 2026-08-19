from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CompositionPreset(StrEnum):
    FACELESS_HERO = "FACELESS_HERO"
    EDITORIAL_CROP = "EDITORIAL_CROP"
    REAR = "REAR"
    THREE_QUARTER_REAR = "THREE_QUARTER_REAR"
    STREET_SNAP = "STREET_SNAP"
    DETAIL_EDITORIAL = "DETAIL_EDITORIAL"


class ImageGenerationStatus(StrEnum):
    PENDING = "PENDING"
    GENERATING = "GENERATING"
    GENERATED = "GENERATED"
    FAILED = "FAILED"


class ImageGenerationPrompt(BaseModel):
    model_config = ConfigDict(frozen=True)

    target_date: date
    composition: CompositionPreset
    scene: str = Field(min_length=3, max_length=160)
    text: str = Field(min_length=100, max_length=8_000)


class GeneratedImagePayload(BaseModel):
    """Provider-neutral encoded image payload; provider response schemas stop here."""

    model_config = ConfigDict(frozen=True)

    image_base64: str = Field(min_length=1)


class GeneratedImage(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int | None = None
    target_date: date
    recipe_target_date: date
    model: str = Field(min_length=1, max_length=128)
    prompt: str = Field(min_length=100, max_length=8_000)
    composition: CompositionPreset
    scene: str = Field(min_length=3, max_length=160)
    generation_size: str = Field(pattern=r"^\d{3,4}x\d{3,4}$")
    final_width: int | None = Field(default=None, gt=0)
    final_height: int | None = Field(default=None, gt=0)
    file_path: str | None = Field(default=None, min_length=1, max_length=512)
    status: ImageGenerationStatus
    error_code: str | None = Field(default=None, max_length=64)
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def validate_state(self) -> GeneratedImage:
        if self.status is ImageGenerationStatus.GENERATED:
            if self.file_path is None or self.final_width is None or self.final_height is None:
                raise ValueError("generated images require file metadata")
        if self.status is ImageGenerationStatus.FAILED and self.error_code is None:
            raise ValueError("failed images require an error code")
        return self
