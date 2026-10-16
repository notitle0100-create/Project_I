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


class ArtDirectionPreset(StrEnum):
    PINTEREST_STREET = "PINTEREST_STREET"
    CLEAN_ARCHITECTURAL = "CLEAN_ARCHITECTURAL"
    CANDID_URBAN = "CANDID_URBAN"
    LOW_ANGLE_EDITORIAL = "LOW_ANGLE_EDITORIAL"
    TEXTURED_STREET = "TEXTURED_STREET"


class Pose(StrEnum):
    WEIGHT_SHIFT = "weight_shift"
    STEP_FORWARD = "step_forward"
    WALKING = "walking"
    HANDS_IN_POCKETS = "hands_in_pockets"
    ADJUSTING_OUTER = "adjusting_outer"
    HOLDING_BAG_LOW = "holding_bag_low"
    TURNED_TORSO = "turned_torso"


class BodyAngle(StrEnum):
    FRONT = "front"
    THREE_QUARTER = "three_quarter"
    SIDE = "side"
    REAR = "rear"


class CameraHeight(StrEnum):
    WAIST = "waist"
    CHEST = "chest"
    EYE = "eye"
    SLIGHT_LOW = "slight_low"


class CameraDistance(StrEnum):
    MEDIUM_FULL = "medium_full"
    CLOSE_EDITORIAL = "close_editorial"


class SubjectPosition(StrEnum):
    CENTER = "center"
    LEFT_THIRD = "left_third"
    RIGHT_THIRD = "right_third"


class NegativeSpace(StrEnum):
    LEFT = "left"
    RIGHT = "right"
    UPPER = "upper"
    ENVIRONMENTAL = "environmental"


class BackgroundTexture(StrEnum):
    BRICK = "brick"
    CONCRETE = "concrete"
    GLASS_METAL = "glass_metal"
    CAFE = "cafe"
    PARKING = "parking"
    SIDEWALK = "sidewalk"
    TEXTURED_WALL = "textured_wall"


class BackgroundClarity(StrEnum):
    MODERATE = "moderate"
    SOFT = "soft"
    CRISP = "crisp"


class Lighting(StrEnum):
    SOFT_DAYLIGHT = "soft_daylight"
    OVERCAST_DAYLIGHT = "overcast_daylight"
    AVAILABLE_LIGHT = "available_light"
    WARM_INTERIOR = "warm_interior"


class EditorialMood(StrEnum):
    CANDID = "candid"
    QUIET = "quiet"
    RAW = "raw"
    INTIMATE = "intimate"
    SUBDUED = "subdued"


class ScenePreset(StrEnum):
    CONCRETE_STOREFRONT = "concrete storefront"
    NARROW_URBAN_STREET = "narrow urban street"
    GLASS_METAL_ARCHITECTURE = "glass-metal architecture"
    SUBDUED_CAFE_EXTERIOR = "subdued cafe exterior"
    PARKING_STRUCTURE = "parking structure"
    QUIET_SIDEWALK = "quiet sidewalk"
    TEXTURED_URBAN_WALL = "textured wall / urban structure"


class ArtDirection(BaseModel):
    model_config = ConfigDict(frozen=True)

    preset: ArtDirectionPreset
    pose: Pose
    body_angle: BodyAngle
    camera_height: CameraHeight
    camera_distance: CameraDistance
    subject_position: SubjectPosition
    outfit_frame_occupancy: int = Field(ge=65, le=80)
    negative_space: NegativeSpace
    background_texture: BackgroundTexture
    background_clarity: BackgroundClarity
    lighting: Lighting
    editorial_mood: EditorialMood


class ImageGenerationStatus(StrEnum):
    PENDING = "PENDING"
    GENERATING = "GENERATING"
    GENERATED = "GENERATED"
    FAILED = "FAILED"


class ReferenceImage(BaseModel):
    """A validated, conditioned image held in memory for one Cloudflare request."""

    model_config = ConfigDict(frozen=True)

    filename: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*\.png$")
    content: bytes = Field(min_length=1, max_length=4_000_000)


class ImageGenerationPrompt(BaseModel):
    model_config = ConfigDict(frozen=True)

    target_date: date
    composition: CompositionPreset
    scene: ScenePreset
    art_direction: ArtDirection
    text: str = Field(min_length=100, max_length=8_000)
    flux_structured_text: str | None = Field(default=None, min_length=100, max_length=8_000)
    reference_images: tuple[ReferenceImage, ...] = Field(default=(), max_length=2)


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
