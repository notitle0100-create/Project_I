from __future__ import annotations

import base64
import binascii
from datetime import date
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, ConfigDict

from seoul_mens_daily_edit.images.domain import GeneratedImagePayload

FINAL_IMAGE_SIZE = (1080, 1350)


class ImageProcessingError(RuntimeError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class ProcessedImage(BaseModel):
    model_config = ConfigDict(frozen=True)

    file_path: str
    width: int
    height: int


class ImageProcessor:
    def __init__(self, generated_images_dir: str | Path, generation_size: str) -> None:
        self._root_dir = Path(generated_images_dir).resolve()
        self._generation_size = _parse_size(generation_size)

    def process(self, payload: GeneratedImagePayload, target_date: date) -> ProcessedImage:
        image_bytes = _decode_image(payload.image_base64)
        try:
            with Image.open(BytesIO(image_bytes)) as source:
                source.load()
                if source.size != self._generation_size:
                    raise ImageProcessingError("unexpected_image_dimensions")
                normalized = source.convert("RGB")
                if source.size != FINAL_IMAGE_SIZE:
                    normalized = normalized.resize(FINAL_IMAGE_SIZE, Image.Resampling.LANCZOS)
        except ImageProcessingError:
            raise
        except (UnidentifiedImageError, OSError) as exc:
            raise ImageProcessingError("invalid_image") from exc

        destination = self._destination_path(target_date)
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            normalized.save(destination, format="PNG")
        except OSError as exc:
            raise ImageProcessingError("filesystem_error") from exc
        try:
            file_path = destination.relative_to(Path.cwd()).as_posix()
        except ValueError:
            file_path = destination.as_posix()
        return ProcessedImage(
            file_path=file_path,
            width=FINAL_IMAGE_SIZE[0],
            height=FINAL_IMAGE_SIZE[1],
        )

    def _destination_path(self, target_date: date) -> Path:
        destination = self._root_dir / target_date.isoformat() / "editorial.png"
        resolved_destination = destination.resolve()
        if self._root_dir not in resolved_destination.parents:
            raise ImageProcessingError("filesystem_error")
        return resolved_destination


def _parse_size(size: str) -> tuple[int, int]:
    try:
        width_text, height_text = size.lower().split("x", maxsplit=1)
        width, height = int(width_text), int(height_text)
    except (AttributeError, ValueError) as exc:
        raise ValueError("generation size must use WIDTHxHEIGHT") from exc
    if width < 1 or height < 1:
        raise ValueError("generation size dimensions must be positive")
    return width, height


def _decode_image(encoded_image: str) -> bytes:
    try:
        return base64.b64decode(encoded_image, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ImageProcessingError("invalid_image") from exc
