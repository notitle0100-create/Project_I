from __future__ import annotations

from dataclasses import dataclass

from seoul_mens_daily_edit.outfits.domain import (
    Accessory,
    AccessoryCategory,
    Bag,
    BagCategory,
    Bottom,
    BottomCategory,
    BottomFit,
    Color,
    Outerwear,
    OuterwearCategory,
    OuterwearFit,
    OutfitRecipe,
    ShoeCategory,
    Shoes,
    Top,
    TopCategory,
    TopFit,
)
from seoul_mens_daily_edit.styling.domain import StylePreset, StyleSelection
from seoul_mens_daily_edit.weather.domain import TemperatureBand, WeatherSnapshot, get_styling_hints

RECENT_RECIPE_LIMIT = 8
MAX_RECIPE_CANDIDATES = 3
MAX_ACCESSORIES_BY_STYLE: dict[StylePreset, int] = {
    StylePreset.SOFT_BOYFRIEND: 1,
    StylePreset.MINIMAL: 0,
    StylePreset.AMEKAJI: 1,
    StylePreset.OTAKU_GRUNGE: 2,
}


@dataclass(frozen=True)
class StyleBase:
    top: Top
    bottom: Bottom
    shoes: Shoes
    bag: Bag | None
    accessories: tuple[Accessory, ...]
    palette: tuple[Color, ...]
    notes: tuple[str, ...]


STYLE_BASES: dict[StylePreset, tuple[StyleBase, ...]] = {
    StylePreset.SOFT_BOYFRIEND: (
        StyleBase(
            top=Top(
                category=TopCategory.SHIRT,
                fit=TopFit.RELAXED,
                color=Color.OFF_WHITE,
                description="soft relaxed shirt",
            ),
            bottom=Bottom(
                category=BottomCategory.TROUSERS,
                fit=BottomFit.STRAIGHT,
                color=Color.TAUPE,
                description="clean straight trousers",
            ),
            shoes=Shoes(
                category=ShoeCategory.SNEAKERS,
                color=Color.WHITE,
                description="clean low-profile sneakers",
            ),
            bag=Bag(
                category=BagCategory.SHOULDER_BAG,
                color=Color.TAUPE,
                description="understated shoulder bag",
            ),
            accessories=(),
            palette=(Color.OFF_WHITE, Color.TAUPE, Color.WHITE),
            notes=("Keep the silhouette relaxed with a clean finish.",),
        ),
        StyleBase(
            top=Top(
                category=TopCategory.KNIT,
                fit=TopFit.REGULAR,
                color=Color.BEIGE,
                description="soft fine-gauge knit",
            ),
            bottom=Bottom(
                category=BottomCategory.DENIM,
                fit=BottomFit.WIDE_STRAIGHT,
                color=Color.INDIGO,
                description="relaxed straight denim",
            ),
            shoes=Shoes(
                category=ShoeCategory.SNEAKERS,
                color=Color.OFF_WHITE,
                description="simple canvas sneakers",
            ),
            bag=Bag(category=BagCategory.TOTE_BAG, color=Color.BEIGE, description="plain tote bag"),
            accessories=(
                Accessory(
                    category=AccessoryCategory.WATCH, color=Color.BROWN, description="simple watch"
                ),
            ),
            palette=(Color.BEIGE, Color.INDIGO, Color.OFF_WHITE),
            notes=("Use one soft texture as the focal point.",),
        ),
    ),
    StylePreset.MINIMAL: (
        StyleBase(
            top=Top(
                category=TopCategory.SHIRT,
                fit=TopFit.REGULAR,
                color=Color.WHITE,
                description="clean structured shirt",
            ),
            bottom=Bottom(
                category=BottomCategory.TROUSERS,
                fit=BottomFit.STRAIGHT,
                color=Color.CHARCOAL,
                description="structured straight trousers",
            ),
            shoes=Shoes(
                category=ShoeCategory.LEATHER_SHOES,
                color=Color.BLACK,
                description="restrained leather shoes",
            ),
            bag=Bag(
                category=BagCategory.CROSSBODY_BAG,
                color=Color.BLACK,
                description="minimal crossbody bag",
            ),
            accessories=(),
            palette=(Color.WHITE, Color.CHARCOAL, Color.BLACK),
            notes=("Maintain low visual noise and clean lines.",),
        ),
        StyleBase(
            top=Top(
                category=TopCategory.LONG_SLEEVE_TEE,
                fit=TopFit.REGULAR,
                color=Color.GRAY,
                description="plain long-sleeve top",
            ),
            bottom=Bottom(
                category=BottomCategory.TROUSERS,
                fit=BottomFit.TAPERED,
                color=Color.NAVY,
                description="simple tapered trousers",
            ),
            shoes=Shoes(
                category=ShoeCategory.SNEAKERS,
                color=Color.WHITE,
                description="unbranded clean sneakers",
            ),
            bag=None,
            accessories=(),
            palette=(Color.GRAY, Color.NAVY, Color.WHITE),
            notes=("Avoid graphics and unnecessary accessories.",),
        ),
    ),
    StylePreset.AMEKAJI: (
        StyleBase(
            top=Top(
                category=TopCategory.SHIRT,
                fit=TopFit.RELAXED,
                color=Color.MUTED_GREEN,
                description="wearable flannel shirt",
            ),
            bottom=Bottom(
                category=BottomCategory.FATIGUE_PANTS,
                fit=BottomFit.RELAXED,
                color=Color.OLIVE,
                description="relaxed fatigue pants",
            ),
            shoes=Shoes(
                category=ShoeCategory.BOOTS, color=Color.BROWN, description="plain leather boots"
            ),
            bag=Bag(
                category=BagCategory.TOTE_BAG, color=Color.KHAKI, description="canvas tote bag"
            ),
            accessories=(
                Accessory(
                    category=AccessoryCategory.WATCH, color=Color.BROWN, description="durable watch"
                ),
            ),
            palette=(Color.MUTED_GREEN, Color.OLIVE, Color.BROWN),
            notes=("Keep heritage details casual and everyday-ready.",),
        ),
        StyleBase(
            top=Top(
                category=TopCategory.SWEATSHIRT,
                fit=TopFit.REGULAR,
                color=Color.OFF_WHITE,
                description="plain heavyweight sweatshirt",
            ),
            bottom=Bottom(
                category=BottomCategory.DENIM,
                fit=BottomFit.STRAIGHT,
                color=Color.INDIGO,
                description="straight denim",
            ),
            shoes=Shoes(
                category=ShoeCategory.SNEAKERS,
                color=Color.NAVY,
                description="durable casual sneakers",
            ),
            bag=Bag(
                category=BagCategory.CROSSBODY_BAG,
                color=Color.KHAKI,
                description="canvas crossbody bag",
            ),
            accessories=(),
            palette=(Color.OFF_WHITE, Color.INDIGO, Color.KHAKI),
            notes=("Use workwear references without costume reconstruction.",),
        ),
    ),
    StylePreset.OTAKU_GRUNGE: (
        StyleBase(
            top=Top(
                category=TopCategory.LONG_SLEEVE_TEE,
                fit=TopFit.RELAXED,
                color=Color.CHARCOAL,
                description="dark abstract graphic long-sleeve tee",
            ),
            bottom=Bottom(
                category=BottomCategory.DENIM,
                fit=BottomFit.WIDE_STRAIGHT,
                color=Color.INDIGO,
                description="relaxed washed denim",
            ),
            shoes=Shoes(
                category=ShoeCategory.CHUNKY_SNEAKERS,
                color=Color.BLACK,
                description="chunky black sneakers",
            ),
            bag=Bag(
                category=BagCategory.CROSSBODY_BAG,
                color=Color.BLACK,
                description="compact black crossbody bag",
            ),
            accessories=(
                Accessory(
                    category=AccessoryCategory.KEYRING,
                    color=Color.MUTED_BLUE,
                    description="restrained keyring detail",
                ),
            ),
            palette=(Color.CHARCOAL, Color.INDIGO, Color.MUTED_BLUE),
            notes=("Use an original abstract graphic, never a character or costume reference.",),
        ),
        StyleBase(
            top=Top(
                category=TopCategory.HOODIE,
                fit=TopFit.RELAXED,
                color=Color.OFF_WHITE,
                description="light relaxed hoodie",
            ),
            bottom=Bottom(
                category=BottomCategory.CARGO_PANTS,
                fit=BottomFit.WIDE_STRAIGHT,
                color=Color.BLACK,
                description="loose black cargo pants",
            ),
            shoes=Shoes(
                category=ShoeCategory.CHUNKY_SNEAKERS,
                color=Color.BLACK,
                description="chunky dark sneakers",
            ),
            bag=Bag(
                category=BagCategory.SHOULDER_BAG,
                color=Color.CHARCOAL,
                description="small charcoal shoulder bag",
            ),
            accessories=(
                Accessory(
                    category=AccessoryCategory.CHAIN,
                    color=Color.GRAY,
                    description="single restrained chain",
                ),
            ),
            palette=(Color.BLACK, Color.OFF_WHITE, Color.CHARCOAL),
            notes=("Favor a long, loose silhouette with controlled dark-on-light contrast.",),
        ),
    ),
}


def build_recipe_candidates(
    weather_snapshot: WeatherSnapshot,
    style_selection: StyleSelection,
) -> tuple[OutfitRecipe, ...]:
    hints = get_styling_hints(weather_snapshot)
    bases = STYLE_BASES[style_selection.style]
    start = style_selection.target_date.toordinal() % len(bases)
    candidates: list[OutfitRecipe] = []
    for offset in range(MAX_RECIPE_CANDIDATES):
        base = bases[(start + offset) % len(bases)]
        candidates.append(
            _build_recipe(
                weather_snapshot,
                style_selection,
                base,
                hints.temperature_band,
                hints.layering_recommended,
                hints.rain_sensitive,
            )
        )
    return tuple(candidates)


def select_recipe_candidate(
    candidates: tuple[OutfitRecipe, ...],
    recent_signatures: set[tuple[str, str, str, tuple[str, ...], str | None, str]],
    weather_snapshot: WeatherSnapshot,
) -> OutfitRecipe:
    valid_candidates = [
        candidate
        for candidate in candidates
        if not validate_recipe_for_weather(candidate, weather_snapshot)
    ]
    if not valid_candidates:
        raise ValueError("no valid outfit recipe candidates")
    for candidate in valid_candidates:
        if candidate.signature not in recent_signatures:
            return candidate
    return valid_candidates[0]


def validate_recipe_for_weather(
    recipe: OutfitRecipe, weather_snapshot: WeatherSnapshot
) -> tuple[str, ...]:
    hints = get_styling_hints(weather_snapshot)
    errors: list[str] = []
    if hints.temperature_band in {TemperatureBand.VERY_HOT, TemperatureBand.WARM}:
        if recipe.outer is not None:
            errors.append("hot weather must not include outerwear")
        if recipe.top.category in {TopCategory.KNIT, TopCategory.SWEATSHIRT, TopCategory.HOODIE}:
            errors.append("hot weather must not include heavy top layers")
    if (
        hints.temperature_band
        in {TemperatureBand.COLD, TemperatureBand.VERY_COLD, TemperatureBand.FREEZING}
        and recipe.outer is None
    ):
        errors.append("cold weather requires outerwear")
    if (
        hints.temperature_band is TemperatureBand.FREEZING
        and recipe.outer is not None
        and recipe.outer.category not in {OuterwearCategory.COAT, OuterwearCategory.PUFFER}
    ):
        errors.append("freezing weather requires a coat or puffer")
    if len(recipe.accessories) > MAX_ACCESSORIES_BY_STYLE[recipe.style]:
        errors.append("accessory count exceeds style limit")
    return tuple(errors)


def _build_recipe(
    weather_snapshot: WeatherSnapshot,
    selection: StyleSelection,
    base: StyleBase,
    temperature_band: TemperatureBand,
    layering_recommended: bool,
    rain_sensitive: bool,
) -> OutfitRecipe:
    top = _top_for_temperature(base.top, temperature_band)
    bottom = base.bottom
    if selection.style is StylePreset.OTAKU_GRUNGE and temperature_band in {
        TemperatureBand.COLD,
        TemperatureBand.VERY_COLD,
        TemperatureBand.FREEZING,
    }:
        top = Top(
            category=TopCategory.HOODIE,
            fit=TopFit.RELAXED,
            color=Color.OFF_WHITE,
            description="light relaxed hoodie",
        )
        bottom = Bottom(
            category=BottomCategory.DENIM,
            fit=BottomFit.WIDE_STRAIGHT,
            color=Color.INDIGO,
            description="relaxed washed denim",
        )
    outer = _outer_for_temperature(selection.style, temperature_band, layering_recommended)
    palette = _palette_for_recipe(
        base.palette, top.color, outer.color if outer is not None else None
    )
    notes = list(base.notes)
    if layering_recommended:
        notes.append("Choose the outer layer so it can be removed as temperatures change.")
    if rain_sensitive:
        notes.append("Keep the trouser hem clear of standing water and favor easy-care layers.")
    return OutfitRecipe(
        target_date=weather_snapshot.target_date,
        style=selection.style,
        occasion=selection.occasion,
        mood=selection.mood,
        top=top,
        bottom=bottom,
        outer=outer,
        shoes=base.shoes,
        bag=base.bag,
        accessories=base.accessories,
        palette=palette,
        layering_depth=_layering_depth(temperature_band, outer),
        styling_notes=tuple(notes),
    )


def _top_for_temperature(top: Top, temperature_band: TemperatureBand) -> Top:
    if temperature_band in {TemperatureBand.VERY_HOT, TemperatureBand.WARM}:
        return Top(
            category=TopCategory.TEE,
            fit=TopFit.REGULAR,
            color=top.color,
            description="breathable plain tee",
        )
    return top


def _outer_for_temperature(
    style: StylePreset,
    temperature_band: TemperatureBand,
    layering_recommended: bool,
) -> Outerwear | None:
    if temperature_band in {TemperatureBand.VERY_HOT, TemperatureBand.WARM}:
        return None
    if temperature_band is TemperatureBand.MILD:
        if not layering_recommended:
            return None
        if style is StylePreset.OTAKU_GRUNGE:
            return Outerwear(
                category=OuterwearCategory.BLAZER,
                fit=OuterwearFit.RELAXED,
                color=Color.BLACK,
                description="relaxed black blazer",
            )
        return Outerwear(
            category=OuterwearCategory.LIGHT_JACKET,
            fit=OuterwearFit.REGULAR,
            color=Color.NAVY,
            description="removable light jacket",
        )
    if temperature_band is TemperatureBand.COOL:
        if style is StylePreset.OTAKU_GRUNGE:
            return Outerwear(
                category=OuterwearCategory.BLAZER,
                fit=OuterwearFit.RELAXED,
                color=Color.BLACK,
                description="relaxed black blazer",
            )
        return Outerwear(
            category=OuterwearCategory.CARDIGAN,
            fit=OuterwearFit.REGULAR,
            color=Color.GRAY,
            description="removable cardigan layer",
        )
    if temperature_band is TemperatureBand.CHILLY:
        category = (
            OuterwearCategory.DENIM_JACKET
            if style is StylePreset.AMEKAJI
            else OuterwearCategory.LIGHT_JACKET
        )
        return Outerwear(
            category=category,
            fit=OuterwearFit.RELAXED,
            color=Color.CHARCOAL,
            description="layered casual jacket",
        )
    if temperature_band is TemperatureBand.COLD:
        if style is StylePreset.OTAKU_GRUNGE:
            return Outerwear(
                category=OuterwearCategory.PUFFER,
                fit=OuterwearFit.LONG,
                color=Color.BLACK,
                description="long black padded outer layer",
            )
        return Outerwear(
            category=OuterwearCategory.COAT,
            fit=OuterwearFit.REGULAR,
            color=Color.NAVY,
            description="proper weather-ready coat",
        )
    if temperature_band is TemperatureBand.VERY_COLD:
        if style is StylePreset.OTAKU_GRUNGE:
            return Outerwear(
                category=OuterwearCategory.PUFFER,
                fit=OuterwearFit.LONG,
                color=Color.BLACK,
                description="long black padded outer layer",
            )
        return Outerwear(
            category=OuterwearCategory.COAT,
            fit=OuterwearFit.LONG,
            color=Color.BLACK,
            description="long warm coat",
        )
    return Outerwear(
        category=OuterwearCategory.PUFFER,
        fit=OuterwearFit.LONG,
        color=Color.BLACK,
        description="long padded outer layer",
    )


def _palette_for_recipe(
    base_palette: tuple[Color, ...], top_color: Color, outer_color: Color | None
) -> tuple[Color, ...]:
    colors = [top_color, *base_palette]
    if outer_color is not None:
        colors.append(outer_color)
    unique: list[Color] = []
    for color in colors:
        if color not in unique:
            unique.append(color)
    return tuple(unique[:3])


def _layering_depth(temperature_band: TemperatureBand, outer: Outerwear | None) -> int:
    if outer is None:
        return 1
    if temperature_band in {TemperatureBand.VERY_COLD, TemperatureBand.FREEZING}:
        return 3
    return 2
