from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, ConfigDict, Field

from seoul_mens_daily_edit.images.domain import ReferenceImage

MAX_REFERENCE_DIMENSION = 511


class ReferenceConditioningError(RuntimeError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class ConditionedReference(BaseModel):
    """Local audit metadata plus request-safe PNG content for the calibration spike."""

    model_config = ConfigDict(frozen=True)

    reference_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    file_path: str
    original_size: tuple[int, int]
    crop_top_px: int = Field(ge=0)
    conditioned_size: tuple[int, int]
    image: ReferenceImage


class ReferenceImageConditioner:
    """Creates head-out, <=511px PNG copies without mutating a source reference."""

    def __init__(self, conditioned_references_dir: str | Path) -> None:
        self._root_dir = Path(conditioned_references_dir).resolve()

    def condition(
        self,
        source_path: str | Path,
        *,
        reference_id: str,
        crop_top_px: int,
    ) -> ConditionedReference:
        source = Path(source_path).resolve(strict=False)
        if not source.is_file():
            raise ReferenceConditioningError("reference_not_found")
        if crop_top_px < 0:
            raise ReferenceConditioningError("invalid_reference_crop")

        try:
            with Image.open(source) as opened:
                opened.load()
                original_size = opened.size
                if crop_top_px >= opened.height:
                    raise ReferenceConditioningError("invalid_reference_crop")
                cropped = opened.crop((0, crop_top_px, opened.width, opened.height)).convert("RGB")
                cropped.thumbnail(
                    (MAX_REFERENCE_DIMENSION, MAX_REFERENCE_DIMENSION), Image.Resampling.LANCZOS
                )
                image_bytes = _encode_png(cropped)
        except ReferenceConditioningError:
            raise
        except (UnidentifiedImageError, OSError) as exc:
            raise ReferenceConditioningError("invalid_reference_image") from exc

        destination = self._destination_path(reference_id)
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(image_bytes)
        except OSError as exc:
            raise ReferenceConditioningError("reference_filesystem_error") from exc

        try:
            file_path = destination.relative_to(Path.cwd()).as_posix()
        except ValueError:
            file_path = destination.as_posix()
        return ConditionedReference(
            reference_id=reference_id,
            file_path=file_path,
            original_size=original_size,
            crop_top_px=crop_top_px,
            conditioned_size=cropped.size,
            image=ReferenceImage(filename=f"{reference_id}.png", content=image_bytes),
        )

    def _destination_path(self, reference_id: str) -> Path:
        destination = self._root_dir / f"{reference_id}.png"
        resolved_destination = destination.resolve()
        if self._root_dir not in resolved_destination.parents:
            raise ReferenceConditioningError("reference_filesystem_error")
        return resolved_destination


def _encode_png(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()
