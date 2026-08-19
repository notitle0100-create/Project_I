from __future__ import annotations

from seoul_mens_daily_edit.images.domain import GeneratedImage, ImageGenerationStatus
from seoul_mens_daily_edit.images.policy import (
    RECENT_COMPOSITION_LIMIT,
    RECENT_SCENE_LIMIT,
    select_composition,
    select_scene,
)
from seoul_mens_daily_edit.images.processor import ImageProcessingError, ImageProcessor
from seoul_mens_daily_edit.images.prompt_builder import (
    ImagePromptBuilder,
    validate_image_context,
)
from seoul_mens_daily_edit.images.provider import ImageProvider, ImageProviderError
from seoul_mens_daily_edit.images.repository import ImageGenerationRepository
from seoul_mens_daily_edit.outfits.domain import OutfitRecipe
from seoul_mens_daily_edit.styling.domain import StyleSelection
from seoul_mens_daily_edit.weather.domain import WeatherSnapshot


class ImageGenerationError(RuntimeError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class ImageGenerationService:
    def __init__(
        self,
        repository: ImageGenerationRepository,
        prompt_builder: ImagePromptBuilder,
        provider: ImageProvider,
        processor: ImageProcessor,
        *,
        model: str,
        generation_size: str,
    ) -> None:
        self._repository = repository
        self._prompt_builder = prompt_builder
        self._provider = provider
        self._processor = processor
        self._model = model
        self._generation_size = generation_size

    def generate(
        self,
        weather_snapshot: WeatherSnapshot,
        style_selection: StyleSelection,
        outfit_recipe: OutfitRecipe,
    ) -> GeneratedImage:
        validate_image_context(weather_snapshot, style_selection, outfit_recipe)
        existing = self._repository.get_by_target_date(outfit_recipe.target_date)
        if existing is not None:
            if existing.status is ImageGenerationStatus.GENERATED:
                return existing
            if existing.status is ImageGenerationStatus.GENERATING:
                raise ImageGenerationError("generation_in_progress")

        composition = select_composition(
            style_selection.style,
            outfit_recipe.target_date,
            self._repository.get_recent_compositions(RECENT_COMPOSITION_LIMIT),
        )
        scene = select_scene(
            style_selection.style,
            outfit_recipe.target_date,
            self._repository.get_recent_scenes(RECENT_SCENE_LIMIT),
        )
        prompt = self._prompt_builder.build(
            weather_snapshot,
            style_selection,
            outfit_recipe,
            composition,
            scene=scene,
        )
        generation = self._repository.begin(
            prompt,
            model=self._model,
            generation_size=self._generation_size,
        )
        if generation.status is ImageGenerationStatus.GENERATED:
            return generation
        if generation.id is None:
            raise ImageGenerationError("generation_record_missing")
        try:
            width, height = _parse_generation_size(self._generation_size)
            payload = self._provider.generate(prompt, width, height)
            processed_image = self._processor.process(payload, outfit_recipe.target_date)
        except ImageProviderError as exc:
            self._repository.mark_failed(generation.id, exc.code)
            raise ImageGenerationError(exc.code) from exc
        except ImageProcessingError as exc:
            self._repository.mark_failed(generation.id, exc.code)
            raise ImageGenerationError(exc.code) from exc
        return self._repository.mark_generated(generation.id, processed_image)


def _parse_generation_size(size: str) -> tuple[int, int]:
    try:
        width_text, height_text = size.lower().split("x", maxsplit=1)
        width, height = int(width_text), int(height_text)
    except (AttributeError, ValueError) as exc:
        raise ValueError("generation_size must use WIDTHxHEIGHT") from exc
    if width < 1 or height < 1:
        raise ValueError("generation_size dimensions must be positive")
    return width, height
