from __future__ import annotations

from dataclasses import dataclass

from seoul_mens_daily_edit.outfits.domain import (
    Accessory,
    AccessoryCategory,
    AccessoryPlacement,
    Bag,
    BagCarryPosition,
    BagCategory,
    Bottom,
    BottomCategory,
    BottomFit,
    BottomStructure,
    Color,
    FootwearShape,
    FootwearWeight,
    LayeringRole,
    LowerVolume,
    OtakuContentAxis,
    OuterLength,
    Outerwear,
    OuterwearCategory,
    OuterwearFit,
    OutfitRecipe,
    PantBreak,
    ShoeCategory,
    Shoes,
    ShoulderShape,
    SilhouetteProfile,
    SilhouetteStrategy,
    TextureProfile,
    Top,
    TopCategory,
    TopFit,
    TopLength,
    TopStructure,
    UpperVolume,
    VisualRole,
)
from seoul_mens_daily_edit.styling.domain import StylePreset, StyleSelection
from seoul_mens_daily_edit.weather.domain import TemperatureBand, WeatherSnapshot, get_styling_hints

RECENT_RECIPE_LIMIT = 8
MAX_RECIPE_CANDIDATES = 3
MAX_ACCESSORIES_BY_STYLE: dict[StylePreset, int] = {
    StylePreset.SOFT_BOYFRIEND: 1,
    StylePreset.MINIMAL: 2,
    StylePreset.AMEKAJI: 2,
    StylePreset.OTAKU_GRUNGE: 2,
}
OTAKU_GRUNGE_CONTENT_AXES = (
    OtakuContentAxis.DETAILED_DARK_TOP,
    OtakuContentAxis.GRAPHIC_FOCAL_TOP,
)


@dataclass(frozen=True)
class StyleBase:
    top: Top
    bottom: Bottom
    shoes: Shoes
    bag: Bag | None
    accessories: tuple[Accessory, ...]
    palette: tuple[Color, ...]
    notes: tuple[str, ...]
    silhouette: SilhouetteProfile
    content_axis: OtakuContentAxis | None = None
    preferred_outer: Outerwear | None = None
    texture_profiles: tuple[TextureProfile, ...] = (TextureProfile.CLEAN_SMOOTH,)
    layering_role: LayeringRole = LayeringRole.SINGLE_RELAXED


def _top(
    category: TopCategory,
    fit: TopFit,
    color: Color,
    *,
    description: str,
    structure: TopStructure = TopStructure.CLEAN_RELAXED,
) -> Top:
    return Top(
        category=category, fit=fit, color=color, description=description, structure=structure
    )


def _bottom(
    category: BottomCategory,
    fit: BottomFit,
    color: Color,
    *,
    description: str,
    structure: BottomStructure = BottomStructure.RELAXED_STRAIGHT_TROUSER,
) -> Bottom:
    return Bottom(
        category=category, fit=fit, color=color, description=description, structure=structure
    )


def _shoes(
    category: ShoeCategory,
    color: Color,
    *,
    description: str,
    shape: FootwearShape = FootwearShape.CLEAN_MINIMAL,
) -> Shoes:
    return Shoes(category=category, color=color, description=description, shape=shape)


def _bag(
    category: BagCategory,
    color: Color,
    *,
    description: str,
    carry_position: BagCarryPosition | None = None,
    visual_role: VisualRole = VisualRole.SUPPORT,
) -> Bag:
    return Bag(
        category=category,
        color=color,
        description=description,
        carry_position=carry_position,
        visual_role=visual_role,
    )


def _accessory(
    category: AccessoryCategory,
    color: Color,
    *,
    description: str,
    placement: AccessoryPlacement | None = None,
    visual_role: VisualRole = VisualRole.SUPPORT,
) -> Accessory:
    return Accessory(
        category=category,
        color=color,
        description=description,
        placement=placement,
        visual_role=visual_role,
    )


def _silhouette(
    strategy: SilhouetteStrategy,
    upper_volume: UpperVolume,
    top_length: TopLength,
    shoulder_shape: ShoulderShape,
    *,
    lower_volume: LowerVolume,
    pant_break: PantBreak,
    footwear_weight: FootwearWeight,
) -> SilhouetteProfile:
    return SilhouetteProfile(
        strategy=strategy,
        upper_volume=upper_volume,
        top_length=top_length,
        shoulder_shape=shoulder_shape,
        lower_volume=lower_volume,
        pant_break=pant_break,
        footwear_weight=footwear_weight,
    )


def _outerwear(
    category: OuterwearCategory,
    fit: OuterwearFit,
    color: Color,
    *,
    description: str,
) -> Outerwear:
    return Outerwear(category=category, fit=fit, color=color, description=description)


STYLE_BASES: dict[StylePreset, tuple[StyleBase, ...]] = {
    StylePreset.SOFT_BOYFRIEND: (
        StyleBase(
            top=_top(
                TopCategory.SHIRT,
                TopFit.RELAXED,
                Color.OFF_WHITE,
                description=(
                    "soft relaxed off-white shirt with tactile drape and an open collar line"
                ),
                structure=TopStructure.SOFT_DRAPED,
            ),
            bottom=_bottom(
                BottomCategory.TROUSERS,
                BottomFit.RELAXED,
                Color.TAUPE,
                description="wide clean taupe trousers with a fluid full break",
                structure=BottomStructure.CLEAN_WIDE_TROUSER,
            ),
            shoes=_shoes(
                ShoeCategory.SNEAKERS,
                Color.BROWN,
                description="soft brown low-profile footwear with an understated silhouette",
                shape=FootwearShape.SOFT_SUEDE_LIKE_SILHOUETTE,
            ),
            bag=None,
            accessories=(),
            palette=(Color.OFF_WHITE, Color.TAUPE, Color.CHARCOAL),
            notes=(
                "Soft texture and relaxed proportion are the focal point, not a basic formula.",
            ),
            silhouette=_silhouette(
                SilhouetteStrategy.STRAIGHT_BALANCED,
                UpperVolume.RELAXED,
                TopLength.STANDARD,
                ShoulderShape.SOFT,
                lower_volume=LowerVolume.RELAXED,
                pant_break=PantBreak.FULL_BREAK,
                footwear_weight=FootwearWeight.LIGHT,
            ),
            texture_profiles=(TextureProfile.SOFT_TACTILE, TextureProfile.CLEAN_SMOOTH),
        ),
        StyleBase(
            top=_top(
                TopCategory.KNIT,
                TopFit.RELAXED,
                Color.OFF_WHITE,
                description="draped off-white knit with a compact hem and soft tactile surface",
                structure=TopStructure.SOFT_DRAPED,
            ),
            bottom=_bottom(
                BottomCategory.DENIM,
                BottomFit.WIDE_STRAIGHT,
                Color.CHARCOAL,
                description="washed charcoal wide denim with a controlled full break",
                structure=BottomStructure.WIDE_FADED_DENIM,
            ),
            shoes=_shoes(
                ShoeCategory.SNEAKERS,
                Color.BLACK,
                description="dark low-profile footwear with quiet visual weight",
                shape=FootwearShape.DARK_LOW_PROFILE,
            ),
            bag=None,
            accessories=(),
            palette=(Color.OFF_WHITE, Color.CHARCOAL, Color.BLACK),
            notes=("Use the soft upper texture against an intentionally wider lower line.",),
            silhouette=_silhouette(
                SilhouetteStrategy.COMPACT_TOP_WIDE_BOTTOM,
                UpperVolume.CLEAN,
                TopLength.SHORT,
                ShoulderShape.NATURAL,
                lower_volume=LowerVolume.WIDE,
                pant_break=PantBreak.FULL_BREAK,
                footwear_weight=FootwearWeight.LIGHT,
            ),
            texture_profiles=(TextureProfile.SOFT_TACTILE, TextureProfile.FADED_DARK),
        ),
        StyleBase(
            top=_top(
                TopCategory.LONG_SLEEVE_TEE,
                TopFit.RELAXED,
                Color.MUTED_BLUE,
                description=(
                    "refined muted-blue relaxed long-sleeve with soft ease through the torso"
                ),
                structure=TopStructure.LONG_LAYERED,
            ),
            bottom=_bottom(
                BottomCategory.TROUSERS,
                BottomFit.RELAXED,
                Color.CHARCOAL,
                description=(
                    "fluid charcoal relaxed straight trousers with clean upper ease and a "
                    "slight break"
                ),
                structure=BottomStructure.RELAXED_STRAIGHT_TROUSER,
            ),
            shoes=_shoes(
                ShoeCategory.LEATHER_SHOES,
                Color.BLACK,
                description="dark low-profile footwear with a clean everyday line",
                shape=FootwearShape.DARK_LOW_PROFILE,
            ),
            bag=None,
            accessories=(
                _accessory(
                    AccessoryCategory.WATCH,
                    Color.BROWN,
                    description="quiet leather-strap watch",
                    placement=AccessoryPlacement.WRIST,
                    visual_role=VisualRole.SUPPORT,
                ),
            ),
            palette=(Color.MUTED_BLUE, Color.CHARCOAL, Color.BLACK),
            notes=("Keep contrast low and let natural drape make the outfit feel intentional.",),
            silhouette=_silhouette(
                SilhouetteStrategy.BOXY_TOP_RELAXED_BOTTOM,
                UpperVolume.BOXY,
                TopLength.STANDARD,
                ShoulderShape.RELAXED,
                lower_volume=LowerVolume.RELAXED,
                pant_break=PantBreak.SLIGHT_BREAK,
                footwear_weight=FootwearWeight.LIGHT,
            ),
            texture_profiles=(TextureProfile.SOFT_TACTILE, TextureProfile.MATTE_TONAL),
            layering_role=LayeringRole.SUBTLE_TONAL_LAYER,
        ),
    ),
    StylePreset.MINIMAL: (
        StyleBase(
            top=_top(
                TopCategory.SHIRT,
                TopFit.REGULAR,
                Color.WHITE,
                description="clean white shirt with a compact structured hem",
            ),
            bottom=_bottom(
                BottomCategory.TROUSERS,
                BottomFit.WIDE_STRAIGHT,
                Color.CHARCOAL,
                description="long charcoal wide trousers with a clean full break",
            ),
            shoes=_shoes(
                ShoeCategory.LEATHER_SHOES,
                Color.BLACK,
                description="tonal medium-weight leather shoes",
            ),
            bag=_bag(
                BagCategory.CROSSBODY_BAG,
                Color.BLACK,
                description="small monochrome crossbody bag",
                carry_position=BagCarryPosition.CROSSBODY_HIGH,
                visual_role=VisualRole.SUPPORT,
            ),
            accessories=(
                _accessory(
                    AccessoryCategory.NECKLACE,
                    Color.GRAY,
                    description="fine silver necklace as a narrow line detail",
                    placement=AccessoryPlacement.NECK,
                    visual_role=VisualRole.SUPPORT,
                ),
            ),
            palette=(Color.WHITE, Color.CHARCOAL, Color.BLACK),
            notes=("Proportion and a clean vertical line create the minimal styling.",),
            silhouette=_silhouette(
                SilhouetteStrategy.COMPACT_TOP_WIDE_BOTTOM,
                UpperVolume.CLEAN,
                TopLength.SHORT,
                ShoulderShape.STRUCTURED,
                lower_volume=LowerVolume.WIDE,
                pant_break=PantBreak.FULL_BREAK,
                footwear_weight=FootwearWeight.MEDIUM,
            ),
        ),
        StyleBase(
            top=_top(
                TopCategory.LONG_SLEEVE_TEE,
                TopFit.REGULAR,
                Color.GRAY,
                description="quiet charcoal-gray long-sleeve top",
            ),
            bottom=_bottom(
                BottomCategory.TROUSERS,
                BottomFit.STRAIGHT,
                Color.NAVY,
                description="fluid deep navy straight trousers with a slight break",
            ),
            shoes=_shoes(
                ShoeCategory.SNEAKERS,
                Color.WHITE,
                description="restrained clean low-profile sneakers",
            ),
            bag=None,
            accessories=(
                _accessory(
                    AccessoryCategory.WATCH,
                    Color.BLACK,
                    description="quiet black watch integrated at the wrist",
                    placement=AccessoryPlacement.WRIST,
                    visual_role=VisualRole.SUPPORT,
                ),
            ),
            palette=(Color.GRAY, Color.NAVY, Color.WHITE),
            notes=("Keep visual noise low while the trouser line provides the design tension.",),
            silhouette=_silhouette(
                SilhouetteStrategy.STRAIGHT_BALANCED,
                UpperVolume.CLEAN,
                TopLength.STANDARD,
                ShoulderShape.NATURAL,
                lower_volume=LowerVolume.STRAIGHT,
                pant_break=PantBreak.SLIGHT_BREAK,
                footwear_weight=FootwearWeight.MEDIUM,
            ),
        ),
        StyleBase(
            top=_top(
                TopCategory.TEE,
                TopFit.RELAXED,
                Color.BLACK,
                description="matte black relaxed tee with a precise shoulder line",
            ),
            bottom=_bottom(
                BottomCategory.TROUSERS,
                BottomFit.WIDE_STRAIGHT,
                Color.BLACK,
                description="long black wide trousers with controlled drape",
            ),
            shoes=_shoes(
                ShoeCategory.LEATHER_SHOES,
                Color.BLACK,
                description="clean tonal leather footwear with medium visual weight",
            ),
            bag=None,
            accessories=(),
            palette=(Color.BLACK, Color.CHARCOAL),
            notes=("Use matte tonal separation and silhouette instead of decorative detail.",),
            silhouette=_silhouette(
                SilhouetteStrategy.RELAXED_TAILORING,
                UpperVolume.STRUCTURED,
                TopLength.STANDARD,
                ShoulderShape.STRUCTURED,
                lower_volume=LowerVolume.WIDE,
                pant_break=PantBreak.FULL_BREAK,
                footwear_weight=FootwearWeight.MEDIUM,
            ),
        ),
    ),
    StylePreset.AMEKAJI: (
        StyleBase(
            top=_top(
                TopCategory.SHIRT,
                TopFit.RELAXED,
                Color.INDIGO,
                description="boxy indigo work shirt with visible workwear texture",
            ),
            bottom=_bottom(
                BottomCategory.FATIGUE_PANTS,
                BottomFit.RELAXED,
                Color.OLIVE,
                description="wide olive fatigue trousers with a deliberate cuff",
            ),
            shoes=_shoes(
                ShoeCategory.BOOTS,
                Color.BROWN,
                description="substantial brown work-boot silhouette",
            ),
            bag=_bag(
                BagCategory.TOTE_BAG,
                Color.KHAKI,
                description="functional canvas tote",
                carry_position=BagCarryPosition.SHOULDER,
                visual_role=VisualRole.SUPPORT,
            ),
            accessories=(
                _accessory(
                    AccessoryCategory.WATCH,
                    Color.BROWN,
                    description="durable workwear watch",
                    placement=AccessoryPlacement.WRIST,
                    visual_role=VisualRole.SUPPORT,
                ),
            ),
            palette=(Color.INDIGO, Color.OLIVE, Color.BROWN),
            notes=(
                "Keep workwear texture practical and contemporary rather than "
                "historical reenactment.",
            ),
            silhouette=_silhouette(
                SilhouetteStrategy.BOXY_TOP_RELAXED_BOTTOM,
                UpperVolume.BOXY,
                TopLength.SHORT,
                ShoulderShape.RELAXED,
                lower_volume=LowerVolume.WIDE,
                pant_break=PantBreak.NO_BREAK,
                footwear_weight=FootwearWeight.HEAVY,
            ),
        ),
        StyleBase(
            top=_top(
                TopCategory.SWEATSHIRT,
                TopFit.REGULAR,
                Color.OFF_WHITE,
                description="compact off-white heavyweight sweatshirt",
            ),
            bottom=_bottom(
                BottomCategory.DENIM,
                BottomFit.WIDE_STRAIGHT,
                Color.INDIGO,
                description="wide indigo denim with a visible rolled hem",
            ),
            shoes=_shoes(
                ShoeCategory.SNEAKERS,
                Color.NAVY,
                description="durable heritage-weight casual sneakers",
            ),
            bag=_bag(
                BagCategory.CROSSBODY_BAG,
                Color.KHAKI,
                description="practical canvas crossbody bag",
                carry_position=BagCarryPosition.CROSSBODY_LOW,
                visual_role=VisualRole.SUPPORT,
            ),
            accessories=(),
            palette=(Color.OFF_WHITE, Color.INDIGO, Color.KHAKI),
            notes=(
                "Use a compact upper and sturdy lower relation without stacking heritage props.",
            ),
            silhouette=_silhouette(
                SilhouetteStrategy.SHORT_OUTER_WIDE_BOTTOM,
                UpperVolume.CLEAN,
                TopLength.SHORT,
                ShoulderShape.NATURAL,
                lower_volume=LowerVolume.WIDE,
                pant_break=PantBreak.NO_BREAK,
                footwear_weight=FootwearWeight.MEDIUM,
            ),
        ),
        StyleBase(
            top=_top(
                TopCategory.TEE,
                TopFit.RELAXED,
                Color.OFF_WHITE,
                description="relaxed ecru tee with a visible waistband",
            ),
            bottom=_bottom(
                BottomCategory.FATIGUE_PANTS,
                BottomFit.RELAXED,
                Color.MUTED_GREEN,
                description="roomy muted-green work trousers with a clean break",
            ),
            shoes=_shoes(
                ShoeCategory.SNEAKERS,
                Color.GRAY,
                description="substantial retro-running sneaker silhouette",
            ),
            bag=None,
            accessories=(
                _accessory(
                    AccessoryCategory.BELT,
                    Color.BROWN,
                    description="simple leather belt at the visible waist",
                    placement=AccessoryPlacement.WAIST,
                    visual_role=VisualRole.SUPPORT,
                ),
            ),
            palette=(Color.OFF_WHITE, Color.MUTED_GREEN, Color.BROWN),
            notes=("Use earth-tone material contrast and a purposeful hem treatment.",),
            silhouette=_silhouette(
                SilhouetteStrategy.COMPACT_TOP_WIDE_BOTTOM,
                UpperVolume.CLEAN,
                TopLength.SHORT,
                ShoulderShape.NATURAL,
                lower_volume=LowerVolume.RELAXED,
                pant_break=PantBreak.SLIGHT_BREAK,
                footwear_weight=FootwearWeight.MEDIUM,
            ),
        ),
    ),
    StylePreset.OTAKU_GRUNGE: (
        StyleBase(
            top=_top(
                TopCategory.LONG_SLEEVE_TEE,
                TopFit.RELAXED,
                Color.CHARCOAL,
                description=(
                    "washed charcoal asymmetric textured long-sleeve with deconstructed seams"
                ),
                structure=TopStructure.WASHED_TEXTURED,
            ),
            bottom=_bottom(
                BottomCategory.DENIM,
                BottomFit.WIDE_STRAIGHT,
                Color.BLACK,
                description="faded wide black denim with natural vertical drape and a full break",
                structure=BottomStructure.WIDE_FADED_DENIM,
            ),
            shoes=_shoes(
                ShoeCategory.CHUNKY_SNEAKERS,
                Color.BLACK,
                description="chunky black sneaker with a substantial rounded sole",
                shape=FootwearShape.CHUNKY_BLACK_SNEAKER,
            ),
            bag=None,
            accessories=(
                _accessory(
                    AccessoryCategory.NECKLACE,
                    Color.GRAY,
                    description="single narrow silver necklace focal point",
                    placement=AccessoryPlacement.NECK,
                    visual_role=VisualRole.FOCAL,
                ),
            ),
            palette=(Color.BLACK, Color.CHARCOAL, Color.GRAY),
            notes=(
                "DETAILED_DARK_TOP: use washed black, charcoal, and matte black texture "
                "contrast; the detailed upper and faded lower create the focal structure, never "
                "costume styling. A bag is intentionally absent.",
            ),
            silhouette=_silhouette(
                SilhouetteStrategy.RELAXED_TAILORING,
                UpperVolume.STRUCTURED,
                TopLength.LONG,
                ShoulderShape.STRUCTURED,
                lower_volume=LowerVolume.RELAXED,
                pant_break=PantBreak.FULL_BREAK,
                footwear_weight=FootwearWeight.MEDIUM,
            ),
            content_axis=OtakuContentAxis.DETAILED_DARK_TOP,
            texture_profiles=(TextureProfile.WASHED_CHARCOAL, TextureProfile.FADED_DARK),
            layering_role=LayeringRole.FOCAL_UPPER_LAYER,
        ),
        StyleBase(
            top=_top(
                TopCategory.SWEATSHIRT,
                TopFit.OVERSIZED,
                Color.CHARCOAL,
                description=(
                    "matte black detailed shirt-jacket with a layered placket and quiet hardware"
                ),
                structure=TopStructure.TAILORED_RELAXED,
            ),
            bottom=_bottom(
                BottomCategory.TROUSERS,
                BottomFit.STRAIGHT,
                Color.BLACK,
                description="distressed black denim with controlled texture and a stacked hem",
                structure=BottomStructure.DISTRESSED_BLACK_DENIM,
            ),
            shoes=_shoes(
                ShoeCategory.LEATHER_SHOES,
                Color.BLACK,
                description="heavy rounded black leather footwear with a grounded silhouette",
                shape=FootwearShape.HEAVY_ROUND_TOE,
            ),
            bag=None,
            accessories=(),
            palette=(Color.CHARCOAL, Color.BLACK, Color.GRAY),
            notes=(
                "DETAILED_DARK_TOP: create upper-texture and lower-line tension with faded "
                "materials; all-black uses tonal separation instead of accessory stacking.",
            ),
            silhouette=_silhouette(
                SilhouetteStrategy.BOXY_TOP_RELAXED_BOTTOM,
                UpperVolume.BOXY,
                TopLength.STANDARD,
                ShoulderShape.RELAXED,
                lower_volume=LowerVolume.STRAIGHT,
                pant_break=PantBreak.STACKED,
                footwear_weight=FootwearWeight.HEAVY,
            ),
            content_axis=OtakuContentAxis.DETAILED_DARK_TOP,
            texture_profiles=(TextureProfile.MATTE_TONAL, TextureProfile.DISTRESSED_DARK_DENIM),
            layering_role=LayeringRole.FOCAL_UPPER_LAYER,
        ),
        StyleBase(
            top=_top(
                TopCategory.TEE,
                TopFit.RELAXED,
                Color.CHARCOAL,
                description=(
                    "washed charcoal original abstract anime-inspired graphic tee with no "
                    "character depiction"
                ),
                structure=TopStructure.GRAPHIC_FOCAL,
            ),
            bottom=_bottom(
                BottomCategory.DENIM,
                BottomFit.RELAXED,
                Color.BLACK,
                description=(
                    "relaxed grunge black denim with a faded surface and intentional hem break"
                ),
                structure=BottomStructure.RELAXED_BLACK_DENIM,
            ),
            shoes=_shoes(
                ShoeCategory.SNEAKERS,
                Color.BLACK,
                description="distressed black low-top footwear with a worn-in silhouette",
                shape=FootwearShape.DISTRESSED_LOW_TOP,
            ),
            bag=None,
            accessories=(
                _accessory(
                    AccessoryCategory.NECKLACE,
                    Color.GRAY,
                    description="one restrained silver necklace at the neck",
                    placement=AccessoryPlacement.NECK,
                    visual_role=VisualRole.SUPPORT,
                ),
            ),
            palette=(Color.CHARCOAL, Color.BLACK, Color.GRAY),
            notes=(
                "GRAPHIC_FOCAL_TOP: use an original abstract or anime-inspired visual grammar, "
                "never a copyrighted character, logo, or cosplay reference; washed and faded "
                "texture contrast keeps the dark layers intentional.",
            ),
            silhouette=_silhouette(
                SilhouetteStrategy.COMPACT_TOP_WIDE_BOTTOM,
                UpperVolume.RELAXED,
                TopLength.STANDARD,
                ShoulderShape.RELAXED,
                lower_volume=LowerVolume.VERY_WIDE,
                pant_break=PantBreak.NO_BREAK,
                footwear_weight=FootwearWeight.HEAVY,
            ),
            content_axis=OtakuContentAxis.GRAPHIC_FOCAL_TOP,
            texture_profiles=(TextureProfile.WASHED_CHARCOAL, TextureProfile.FADED_DARK),
            layering_role=LayeringRole.FOCAL_UPPER_LAYER,
        ),
        StyleBase(
            top=_top(
                TopCategory.TEE,
                TopFit.RELAXED,
                Color.BLACK,
                description=(
                    "matte black original abstract graphic tee with a deliberately placed "
                    "focal print"
                ),
                structure=TopStructure.GRAPHIC_FOCAL,
            ),
            bottom=_bottom(
                BottomCategory.DENIM_BERMUDA,
                BottomFit.WIDE_STRAIGHT,
                Color.MUTED_BLUE,
                description="wide faded denim bermuda with a clean below-knee hem",
                structure=BottomStructure.DENIM_BERMUDA,
            ),
            shoes=_shoes(
                ShoeCategory.BOOTS,
                Color.BROWN,
                description="substantial brown work-boot silhouette with a broad visual base",
                shape=FootwearShape.SUBSTANTIAL_WORK_BOOT,
            ),
            bag=None,
            accessories=(),
            palette=(Color.BLACK, Color.MUTED_BLUE, Color.BROWN),
            notes=(
                "GRAPHIC_FOCAL_TOP: keep the original abstract graphic meaningful and pair it with "
                "one intentionally selected alternative lower, never cosplay or logo reproduction.",
            ),
            silhouette=_silhouette(
                SilhouetteStrategy.COMPACT_TOP_WIDE_BOTTOM,
                UpperVolume.RELAXED,
                TopLength.STANDARD,
                ShoulderShape.RELAXED,
                lower_volume=LowerVolume.VERY_WIDE,
                pant_break=PantBreak.NO_BREAK,
                footwear_weight=FootwearWeight.HEAVY,
            ),
            content_axis=OtakuContentAxis.GRAPHIC_FOCAL_TOP,
            texture_profiles=(TextureProfile.MATTE_TONAL, TextureProfile.FADED_DARK),
            layering_role=LayeringRole.FOCAL_UPPER_LAYER,
        ),
    ),
}


def build_recipe_candidates(
    weather_snapshot: WeatherSnapshot, style_selection: StyleSelection
) -> tuple[OutfitRecipe, ...]:
    hints = get_styling_hints(weather_snapshot)
    bases = STYLE_BASES[style_selection.style]
    start = style_selection.target_date.toordinal() % len(bases)
    return tuple(
        _build_recipe(
            weather_snapshot,
            style_selection,
            bases[(start + offset) % len(bases)],
            hints.temperature_band,
            hints.layering_recommended,
            hints.rain_sensitive,
        )
        for offset in range(MAX_RECIPE_CANDIDATES)
    )


def select_recipe_candidate(
    candidates: tuple[OutfitRecipe, ...],
    recent_signatures: set[tuple[str, ...]],
    weather_snapshot: WeatherSnapshot,
) -> OutfitRecipe:
    valid_candidates = [
        candidate
        for candidate in candidates
        if not validate_recipe_for_weather(candidate, weather_snapshot)
    ]
    if not valid_candidates:
        raise ValueError("no valid outfit recipe candidates")
    valid_candidates = _prefer_non_repeated_otaku_outer(valid_candidates, recent_signatures)
    return next(
        (
            candidate
            for candidate in valid_candidates
            if candidate.signature not in recent_signatures
        ),
        valid_candidates[0],
    )


def _prefer_non_repeated_otaku_outer(
    candidates: list[OutfitRecipe], recent_signatures: set[tuple[str, ...]]
) -> list[OutfitRecipe]:
    """Avoid repeating a blazer/tailored outer when another valid candidate exists."""
    recent_outers = {signature[4] for signature in recent_signatures if len(signature) > 4}
    if "blazer" not in recent_outers:
        return candidates
    without_blazer = [
        candidate
        for candidate in candidates
        if candidate.outer is None or candidate.outer.category is not OuterwearCategory.BLAZER
    ]
    return without_blazer or candidates


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
    outer = _outer_for_temperature(
        selection.style,
        temperature_band,
        layering_recommended,
        preferred_outer=base.preferred_outer,
    )
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
        bottom=base.bottom,
        outer=outer,
        shoes=base.shoes,
        bag=base.bag,
        accessories=base.accessories,
        palette=palette,
        layering_depth=_layering_depth(temperature_band, outer),
        styling_notes=tuple(notes),
        silhouette=_silhouette_for_recipe(base.silhouette, outer, rain_sensitive),
        content_axis=base.content_axis,
        texture_profiles=base.texture_profiles,
        layering_role=base.layering_role,
    )


def _top_for_temperature(top: Top, temperature_band: TemperatureBand) -> Top:
    if temperature_band in {TemperatureBand.VERY_HOT, TemperatureBand.WARM}:
        return _top(
            TopCategory.TEE,
            top.fit if top.fit is not TopFit.OVERSIZED else TopFit.RELAXED,
            top.color,
            description="breathable tee with the base outfit's controlled proportion",
            structure=top.structure,
        )
    return top


def _outer_for_temperature(
    style: StylePreset,
    temperature_band: TemperatureBand,
    layering_recommended: bool,
    *,
    preferred_outer: Outerwear | None = None,
) -> Outerwear | None:
    if temperature_band in {TemperatureBand.VERY_HOT, TemperatureBand.WARM}:
        return None
    if temperature_band is TemperatureBand.MILD:
        if not layering_recommended:
            return None
        if preferred_outer is not None:
            return preferred_outer
        return _outerwear(
            OuterwearCategory.LIGHT_JACKET,
            OuterwearFit.REGULAR,
            Color.NAVY,
            description="removable light jacket",
        )
    if temperature_band is TemperatureBand.COOL:
        if preferred_outer is not None:
            return preferred_outer
        return _outerwear(
            OuterwearCategory.CARDIGAN,
            OuterwearFit.REGULAR,
            Color.GRAY,
            description="removable cardigan layer",
        )
    if temperature_band is TemperatureBand.CHILLY:
        if preferred_outer is not None:
            return preferred_outer
        category = (
            OuterwearCategory.DENIM_JACKET
            if style is StylePreset.AMEKAJI
            else OuterwearCategory.LIGHT_JACKET
        )
        return _outerwear(
            category, OuterwearFit.RELAXED, Color.CHARCOAL, description="layered casual jacket"
        )
    if (
        temperature_band in {TemperatureBand.COLD, TemperatureBand.VERY_COLD}
        and style is StylePreset.OTAKU_GRUNGE
    ):
        return _outerwear(
            OuterwearCategory.PUFFER,
            OuterwearFit.LONG,
            Color.BLACK,
            description="long black padded outer layer with a vertical silhouette",
        )
    if temperature_band is TemperatureBand.COLD:
        return _outerwear(
            OuterwearCategory.COAT,
            OuterwearFit.REGULAR,
            Color.NAVY,
            description="proper weather-ready coat",
        )
    if temperature_band is TemperatureBand.VERY_COLD:
        return _outerwear(
            OuterwearCategory.COAT, OuterwearFit.LONG, Color.BLACK, description="long warm coat"
        )
    return _outerwear(
        OuterwearCategory.PUFFER,
        OuterwearFit.LONG,
        Color.BLACK,
        description="long padded outer layer",
    )


def _silhouette_for_recipe(
    silhouette: SilhouetteProfile,
    outer: Outerwear | None,
    rain_sensitive: bool,
) -> SilhouetteProfile:
    updates: dict[str, object] = {"outer_length": _outer_length(outer)}
    if rain_sensitive and silhouette.pant_break in {PantBreak.FULL_BREAK, PantBreak.STACKED}:
        updates["pant_break"] = PantBreak.SLIGHT_BREAK
    return silhouette.model_copy(update=updates)


def _outer_length(outer: Outerwear | None) -> OuterLength | None:
    if outer is None:
        return None
    if outer.fit is OuterwearFit.LONG:
        return OuterLength.BELOW_KNEE
    if outer.category is OuterwearCategory.BLAZER:
        return OuterLength.HIP
    if outer.category is OuterwearCategory.COAT:
        return OuterLength.THIGH
    return OuterLength.WAIST


def _palette_for_recipe(
    base_palette: tuple[Color, ...], top_color: Color, outer_color: Color | None
) -> tuple[Color, ...]:
    unique: list[Color] = []
    for color in (top_color, *base_palette, outer_color):
        if color is not None and color not in unique:
            unique.append(color)
    return tuple(unique[:3])


def _layering_depth(temperature_band: TemperatureBand, outer: Outerwear | None) -> int:
    if outer is None:
        return 1
    return 3 if temperature_band in {TemperatureBand.VERY_COLD, TemperatureBand.FREEZING} else 2
