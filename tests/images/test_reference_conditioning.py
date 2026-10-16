from __future__ import annotations

import pytest
from PIL import Image

from seoul_mens_daily_edit.images.reference_conditioning import (
    MAX_REFERENCE_DIMENSION,
    ReferenceConditioningError,
    ReferenceImageConditioner,
)


def test_conditioner_creates_head_out_png_copy_without_mutating_source(tmp_path) -> None:
    source = tmp_path / "source.jpg"
    Image.new("RGB", (900, 1200), color="white").save(source, format="JPEG")
    original_bytes = source.read_bytes()
    conditioner = ReferenceImageConditioner(tmp_path / "conditioned")

    result = conditioner.condition(source, reference_id="soft-street", crop_top_px=180)

    assert source.read_bytes() == original_bytes
    assert result.original_size == (900, 1200)
    assert result.crop_top_px == 180
    assert max(result.conditioned_size) == MAX_REFERENCE_DIMENSION
    assert (tmp_path / "conditioned" / "soft-street.png").is_file()
    assert result.image.filename == "soft-street.png"


@pytest.mark.parametrize("crop_top_px", [-1, 1200])
def test_conditioner_rejects_invalid_crop_bounds(tmp_path, crop_top_px: int) -> None:
    source = tmp_path / "source.png"
    Image.new("RGB", (400, 1200), color="white").save(source, format="PNG")

    with pytest.raises(ReferenceConditioningError, match="invalid_reference_crop"):
        ReferenceImageConditioner(tmp_path / "conditioned").condition(
            source, reference_id="invalid-crop", crop_top_px=crop_top_px
        )


def test_conditioner_rejects_invalid_or_missing_sources(tmp_path) -> None:
    conditioner = ReferenceImageConditioner(tmp_path / "conditioned")
    missing = tmp_path / "missing.png"
    invalid = tmp_path / "invalid.txt"
    invalid.write_text("not an image", encoding="utf-8")

    with pytest.raises(ReferenceConditioningError, match="reference_not_found"):
        conditioner.condition(missing, reference_id="missing", crop_top_px=0)
    with pytest.raises(ReferenceConditioningError, match="invalid_reference_image"):
        conditioner.condition(invalid, reference_id="invalid", crop_top_px=0)
