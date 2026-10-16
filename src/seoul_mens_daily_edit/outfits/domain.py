from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from seoul_mens_daily_edit.styling.domain import Mood, Occasion, StylePreset


class Color(StrEnum):
    BLACK = "black"
    CHARCOAL = "charcoal"
    GRAY = "gray"
    OFF_WHITE = "off_white"
    WHITE = "white"
    NAVY = "navy"
    BEIGE = "beige"
    TAUPE = "taupe"
    OLIVE = "olive"
    BROWN = "brown"
    KHAKI = "khaki"
    INDIGO = "indigo"
    MUTED_BLUE = "muted_blue"
    BURGUNDY = "burgundy"
    FADED_RED = "faded_red"
    MUTED_GREEN = "muted_green"


class TopCategory(StrEnum):
    TEE = "tee"
    SHIRT = "shirt"
    LONG_SLEEVE_TEE = "long_sleeve_tee"
    KNIT = "knit"
    SWEATSHIRT = "sweatshirt"
    HOODIE = "hoodie"


class BottomCategory(StrEnum):
    TROUSERS = "trousers"
    DENIM = "denim"
    DENIM_BERMUDA = "denim_bermuda"
    FATIGUE_PANTS = "fatigue_pants"
    CARGO_PANTS = "cargo_pants"


class OuterwearCategory(StrEnum):
    CARDIGAN = "cardigan"
    LIGHT_JACKET = "light_jacket"
    DENIM_JACKET = "denim_jacket"
    WORKWEAR_JACKET = "workwear_jacket"
    BLAZER = "blazer"
    COAT = "coat"
    PUFFER = "puffer"


class ShoeCategory(StrEnum):
    SNEAKERS = "sneakers"
    LEATHER_SHOES = "leather_shoes"
    BOOTS = "boots"
    CHUNKY_SNEAKERS = "chunky_sneakers"


class BagCategory(StrEnum):
    SHOULDER_BAG = "shoulder_bag"
    TOTE_BAG = "tote_bag"
    CROSSBODY_BAG = "crossbody_bag"


class AccessoryCategory(StrEnum):
    CHAIN = "chain"
    KEYRING = "keyring"
    HEADPHONES = "headphones"
    WATCH = "watch"
    NECKLACE = "necklace"
    RING = "ring"
    BELT = "belt"


class TopFit(StrEnum):
    FITTED = "fitted"
    REGULAR = "regular"
    RELAXED = "relaxed"
    OVERSIZED = "oversized"


class TopStructure(StrEnum):
    CLEAN_RELAXED = "clean_relaxed"
    SOFT_DRAPED = "soft_draped"
    BOXY = "boxy"
    SHORT_STRUCTURED = "short_structured"
    LONG_LAYERED = "long_layered"
    TAILORED_RELAXED = "tailored_relaxed"
    WASHED_TEXTURED = "washed_textured"
    GRAPHIC_FOCAL = "graphic_focal"


class BottomFit(StrEnum):
    STRAIGHT = "straight"
    WIDE_STRAIGHT = "wide_straight"
    RELAXED = "relaxed"
    TAPERED = "tapered"


class BottomStructure(StrEnum):
    CLEAN_WIDE_TROUSER = "clean_wide_trouser"
    RELAXED_STRAIGHT_TROUSER = "relaxed_straight_trouser"
    WIDE_FADED_DENIM = "wide_faded_denim"
    RELAXED_BLACK_DENIM = "relaxed_black_denim"
    DISTRESSED_BLACK_DENIM = "distressed_black_denim"
    CLEAN_DARK_SLACKS = "clean_dark_slacks"
    RELAXED_CARGO = "relaxed_cargo"
    DENIM_BERMUDA = "denim_bermuda"


class TextureProfile(StrEnum):
    SOFT_TACTILE = "soft_tactile"
    MATTE_TONAL = "matte_tonal"
    WASHED_CHARCOAL = "washed_charcoal"
    FADED_DARK = "faded_dark"
    DISTRESSED_DARK_DENIM = "distressed_dark_denim"
    CLEAN_SMOOTH = "clean_smooth"


class LayeringRole(StrEnum):
    SINGLE_RELAXED = "single_relaxed"
    SUBTLE_TONAL_LAYER = "subtle_tonal_layer"
    FOCAL_UPPER_LAYER = "focal_upper_layer"


class FootwearShape(StrEnum):
    SLIM_LOW_PROFILE = "slim_low_profile"
    CLEAN_MINIMAL = "clean_minimal"
    SOFT_SUEDE_LIKE_SILHOUETTE = "soft_suede_like_silhouette"
    DARK_LOW_PROFILE = "dark_low_profile"
    LIGHT_STRUCTURED = "light_structured"
    DISTRESSED_LOW_TOP = "distressed_low_top"
    CHUNKY_BLACK_SNEAKER = "chunky_black_sneaker"
    HEAVY_DARK_SNEAKER = "heavy_dark_sneaker"
    SUBSTANTIAL_WORK_BOOT = "substantial_work_boot"
    SHARP_DARK_LEATHER = "sharp_dark_leather"
    HEAVY_ROUND_TOE = "heavy_round_toe"


class OuterwearFit(StrEnum):
    REGULAR = "regular"
    RELAXED = "relaxed"
    OVERSIZED = "oversized"
    LONG = "long"


class UpperVolume(StrEnum):
    CLEAN = "clean"
    RELAXED = "relaxed"
    BOXY = "boxy"
    STRUCTURED = "structured"


class TopLength(StrEnum):
    SHORT = "short"
    STANDARD = "standard"
    LONG = "long"


class ShoulderShape(StrEnum):
    NATURAL = "natural"
    SOFT = "soft"
    RELAXED = "relaxed"
    STRUCTURED = "structured"


class OuterLength(StrEnum):
    WAIST = "waist"
    HIP = "hip"
    THIGH = "thigh"
    BELOW_KNEE = "below_knee"


class LowerVolume(StrEnum):
    STRAIGHT = "straight"
    RELAXED = "relaxed"
    WIDE = "wide"
    VERY_WIDE = "very_wide"


class PantBreak(StrEnum):
    NO_BREAK = "no_break"
    SLIGHT_BREAK = "slight_break"
    FULL_BREAK = "full_break"
    STACKED = "stacked"


class FootwearWeight(StrEnum):
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"


class SilhouetteStrategy(StrEnum):
    COMPACT_TOP_WIDE_BOTTOM = "compact_top_wide_bottom"
    BOXY_TOP_RELAXED_BOTTOM = "boxy_top_relaxed_bottom"
    RELAXED_TAILORING = "relaxed_tailoring"
    LONG_VERTICAL_LAYER = "long_vertical_layer"
    SHORT_OUTER_WIDE_BOTTOM = "short_outer_wide_bottom"
    STRAIGHT_BALANCED = "straight_balanced"
    COLUMN_LAYERING = "column_layering"


class OtakuContentAxis(StrEnum):
    DETAILED_DARK_TOP = "detailed_dark_top"
    GRAPHIC_FOCAL_TOP = "graphic_focal_top"


class VisualRole(StrEnum):
    SUPPORT = "support"
    CONTRAST = "contrast"
    FOCAL = "focal"
    NONE = "none"


class AccessoryPlacement(StrEnum):
    NECK = "neck"
    WAIST = "waist"
    WRIST = "wrist"
    SIDE_HIP = "side_hip"


class BagCarryPosition(StrEnum):
    SHOULDER = "shoulder"
    CROSSBODY_HIGH = "crossbody_high"
    CROSSBODY_LOW = "crossbody_low"
    HANDHELD_LOW = "handheld_low"


class Top(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: TopCategory
    fit: TopFit
    color: Color
    structure: TopStructure = TopStructure.CLEAN_RELAXED
    description: str = Field(min_length=3, max_length=160)


class Bottom(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: BottomCategory
    fit: BottomFit
    color: Color
    structure: BottomStructure = BottomStructure.RELAXED_STRAIGHT_TROUSER
    description: str = Field(min_length=3, max_length=160)


class Outerwear(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: OuterwearCategory
    fit: OuterwearFit
    color: Color
    description: str = Field(min_length=3, max_length=160)


class Shoes(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: ShoeCategory
    color: Color
    shape: FootwearShape = FootwearShape.CLEAN_MINIMAL
    description: str = Field(min_length=3, max_length=160)


class SilhouetteProfile(BaseModel):
    model_config = ConfigDict(frozen=True)

    strategy: SilhouetteStrategy = SilhouetteStrategy.STRAIGHT_BALANCED
    upper_volume: UpperVolume = UpperVolume.CLEAN
    top_length: TopLength = TopLength.STANDARD
    shoulder_shape: ShoulderShape = ShoulderShape.NATURAL
    outer_length: OuterLength | None = None
    lower_volume: LowerVolume = LowerVolume.STRAIGHT
    pant_break: PantBreak = PantBreak.SLIGHT_BREAK
    footwear_weight: FootwearWeight = FootwearWeight.MEDIUM


class Bag(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: BagCategory
    color: Color
    description: str = Field(min_length=3, max_length=160)
    carry_position: BagCarryPosition | None = None
    visual_role: VisualRole = VisualRole.SUPPORT


class Accessory(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: AccessoryCategory
    color: Color
    description: str = Field(min_length=3, max_length=160)
    placement: AccessoryPlacement | None = None
    visual_role: VisualRole = VisualRole.SUPPORT


class OutfitRecipe(BaseModel):
    model_config = ConfigDict(frozen=True)

    target_date: date
    style: StylePreset
    occasion: Occasion
    mood: Mood
    top: Top
    bottom: Bottom
    outer: Outerwear | None
    shoes: Shoes
    bag: Bag | None
    accessories: tuple[Accessory, ...]
    palette: tuple[Color, ...] = Field(min_length=1, max_length=3)
    texture_profiles: tuple[TextureProfile, ...] = Field(
        default=(TextureProfile.CLEAN_SMOOTH,), min_length=1, max_length=3
    )
    layering_role: LayeringRole = LayeringRole.SINGLE_RELAXED
    layering_depth: int = Field(ge=1, le=4)
    styling_notes: tuple[str, ...] = Field(min_length=1, max_length=4)
    silhouette: SilhouetteProfile = Field(default_factory=SilhouetteProfile)
    content_axis: OtakuContentAxis | None = None

    @model_validator(mode="after")
    def validate_recipe(self) -> OutfitRecipe:
        if len(set(self.palette)) != len(self.palette):
            raise ValueError("palette colors must be unique")
        if len(self.accessories) > 2:
            raise ValueError("at most two accessories are allowed")
        if self.outer is None and self.layering_depth != 1:
            raise ValueError("an outfit without outerwear must have layering_depth of 1")
        if self.outer is not None and self.layering_depth < 2:
            raise ValueError("an outfit with outerwear must have layering_depth of at least 2")
        if self.outer is None and self.silhouette.outer_length is not None:
            raise ValueError("silhouette outer_length requires outerwear")
        if self.style is not StylePreset.OTAKU_GRUNGE and self.content_axis is not None:
            raise ValueError("content_axis is only valid for otaku grunge recipes")
        if self.style is StylePreset.SOFT_BOYFRIEND and self.top.fit is TopFit.FITTED:
            raise ValueError("soft boyfriend recipes require a regular or relaxed top fit")
        if (
            self.style is StylePreset.OTAKU_GRUNGE
            and self.content_axis is OtakuContentAxis.GRAPHIC_FOCAL_TOP
            and self.top.structure is not TopStructure.GRAPHIC_FOCAL
        ):
            raise ValueError("graphic focal otaku recipes require a graphic focal top structure")
        if (
            self.style is StylePreset.OTAKU_GRUNGE
            and self.content_axis is OtakuContentAxis.DETAILED_DARK_TOP
            and self.top.structure is TopStructure.GRAPHIC_FOCAL
        ):
            raise ValueError("detailed dark otaku recipes cannot use a graphic focal top structure")
        if (
            self.top.fit is TopFit.OVERSIZED
            and self.outer is not None
            and self.outer.fit is OuterwearFit.OVERSIZED
            and self.silhouette.lower_volume is LowerVolume.VERY_WIDE
            and self.silhouette.footwear_weight is FootwearWeight.HEAVY
        ):
            raise ValueError("all oversized and heavy silhouette combinations are not allowed")
        return self

    @property
    def signature(self) -> tuple[str, ...]:
        return (
            self.style.value,
            self.top.category.value,
            self.bottom.category.value,
            ",".join(color.value for color in self.palette),
            self.outer.category.value if self.outer is not None else "none",
            self.shoes.category.value,
            self.silhouette.strategy.value,
            self.silhouette.pant_break.value,
            self.silhouette.footwear_weight.value,
            self.top.structure.value,
            self.bottom.structure.value,
            self.shoes.shape.value,
            ",".join(profile.value for profile in self.texture_profiles),
            self.layering_role.value,
            self.content_axis.value if self.content_axis is not None else "none",
        )
