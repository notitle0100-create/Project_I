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


class TopFit(StrEnum):
    FITTED = "fitted"
    REGULAR = "regular"
    RELAXED = "relaxed"
    OVERSIZED = "oversized"


class BottomFit(StrEnum):
    STRAIGHT = "straight"
    WIDE_STRAIGHT = "wide_straight"
    RELAXED = "relaxed"
    TAPERED = "tapered"


class OuterwearFit(StrEnum):
    REGULAR = "regular"
    RELAXED = "relaxed"
    OVERSIZED = "oversized"
    LONG = "long"


class Top(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: TopCategory
    fit: TopFit
    color: Color
    description: str = Field(min_length=3, max_length=160)


class Bottom(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: BottomCategory
    fit: BottomFit
    color: Color
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
    description: str = Field(min_length=3, max_length=160)


class Bag(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: BagCategory
    color: Color
    description: str = Field(min_length=3, max_length=160)


class Accessory(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: AccessoryCategory
    color: Color
    description: str = Field(min_length=3, max_length=160)


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
    layering_depth: int = Field(ge=1, le=4)
    styling_notes: tuple[str, ...] = Field(min_length=1, max_length=4)

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
        return self

    @property
    def signature(self) -> tuple[str, str, str, tuple[str, ...], str | None, str]:
        return (
            self.style.value,
            self.top.category.value,
            self.bottom.category.value,
            tuple(color.value for color in self.palette),
            self.outer.category.value if self.outer is not None else None,
            self.shoes.category.value,
        )
