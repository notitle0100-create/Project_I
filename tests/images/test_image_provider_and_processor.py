from __future__ import annotations

import base64
from datetime import date
from io import BytesIO
from types import SimpleNamespace

import httpx
import pytest
from PIL import Image

from seoul_mens_daily_edit.core.config import (
    CLOUDFLARE_KLEIN_4B_MODEL,
    CLOUDFLARE_KLEIN_9B_MODEL,
    Settings,
)
from seoul_mens_daily_edit.images.domain import (
    ArtDirection,
    ArtDirectionPreset,
    BackgroundClarity,
    BackgroundTexture,
    BodyAngle,
    CameraDistance,
    CameraHeight,
    CompositionPreset,
    EditorialMood,
    GeneratedImagePayload,
    ImageGenerationPrompt,
    Lighting,
    NegativeSpace,
    Pose,
    ReferenceImage,
    ScenePreset,
    SubjectPosition,
)
from seoul_mens_daily_edit.images.processor import ImageProcessingError, ImageProcessor
from seoul_mens_daily_edit.images.provider import (
    CloudflareWorkersAIProvider,
    ImageProviderError,
    OpenAIImageProvider,
    create_image_provider,
    get_image_generation_size,
    get_image_model,
)


def make_settings(**overrides: object) -> Settings:
    values = {
        "database_url": "postgresql+psycopg://app:testing-password@localhost:5432/test_database",
        "cloudflare_account_id": "a" * 32,
        "cloudflare_api_token": "test-token-not-a-secret",
        "cloudflare_image_size": "1088x1360",
    }
    values.update(overrides)
    return Settings(**values)


def make_prompt() -> ImageGenerationPrompt:
    return ImageGenerationPrompt(
        target_date=date(2026, 8, 20),
        composition=CompositionPreset.FACELESS_HERO,
        scene=ScenePreset.QUIET_SIDEWALK,
        art_direction=ArtDirection(
            preset=ArtDirectionPreset.PINTEREST_STREET,
            pose=Pose.WEIGHT_SHIFT,
            body_angle=BodyAngle.THREE_QUARTER,
            camera_height=CameraHeight.CHEST,
            camera_distance=CameraDistance.MEDIUM_FULL,
            subject_position=SubjectPosition.RIGHT_THIRD,
            outfit_frame_occupancy=72,
            negative_space=NegativeSpace.LEFT,
            background_texture=BackgroundTexture.SIDEWALK,
            background_clarity=BackgroundClarity.MODERATE,
            lighting=Lighting.SOFT_DAYLIGHT,
            editorial_mood=EditorialMood.CANDID,
        ),
        text="A" * 100,
    )


def test_cloudflare_provider_uses_documented_endpoint_auth_and_multipart_fields() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == (
            "https://api.cloudflare.com/client/v4/accounts/"
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/ai/run/"
            "@cf/black-forest-labs/flux-2-klein-4b"
        )
        assert request.headers["Authorization"] == "Bearer test-token-not-a-secret"
        assert request.headers["Content-Type"].startswith("multipart/form-data; boundary=")
        assert b'name="prompt"' in request.content
        assert b'name="width"' in request.content and b"1088" in request.content
        assert b'name="height"' in request.content and b"1360" in request.content
        return httpx.Response(
            200,
            json={"success": True, "result": {"image": "encoded-image"}},
            request=request,
        )

    provider = CloudflareWorkersAIProvider(
        make_settings(), client=httpx.Client(transport=httpx.MockTransport(handler))
    )

    payload = provider.generate(make_prompt(), 1088, 1360)

    assert payload == GeneratedImagePayload(image_base64="encoded-image")


def test_cloudflare_provider_uses_structured_flux_prompt_and_optional_guidance() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert b'{"composition":"neck-down framing"}' in request.content
        assert b'name="guidance"' in request.content and b"4.5" in request.content
        return httpx.Response(
            200,
            json={"success": True, "result": {"image": "encoded-image"}},
            request=request,
        )

    prompt = make_prompt().model_copy(
        update={"flux_structured_text": '{"composition":"neck-down framing"}'}
    )
    provider = CloudflareWorkersAIProvider(
        make_settings(cloudflare_image_guidance=4.5),
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert provider.generate(prompt, 1088, 1360).image_base64 == "encoded-image"


def test_cloudflare_provider_uses_the_documented_klein_9b_endpoint() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith(f"/ai/run/{CLOUDFLARE_KLEIN_9B_MODEL}")
        assert b'name="seed"' in request.content and b"20260829" in request.content
        return httpx.Response(
            200,
            json={"success": True, "result": {"image": "encoded-image"}},
            request=request,
        )

    provider = CloudflareWorkersAIProvider(
        make_settings(
            cloudflare_image_model=CLOUDFLARE_KLEIN_9B_MODEL, cloudflare_image_seed=20260829
        ),
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert provider.generate(make_prompt(), 1088, 1360).image_base64 == "encoded-image"


def test_model_ab_request_changes_only_the_model_with_a_shared_seed_and_references() -> None:
    prompt = make_prompt().model_copy(
        update={
            "reference_images": (
                ReferenceImage(filename="soft-street.png", content=make_png_bytes((400, 400))),
            )
        }
    )
    four_b = CloudflareWorkersAIProvider(
        make_settings(
            cloudflare_image_model=CLOUDFLARE_KLEIN_4B_MODEL, cloudflare_image_seed=20260829
        )
    )
    nine_b = CloudflareWorkersAIProvider(
        make_settings(
            cloudflare_image_model=CLOUDFLARE_KLEIN_9B_MODEL, cloudflare_image_seed=20260829
        )
    )

    assert four_b._multipart_fields(prompt, 1088, 1360) == nine_b._multipart_fields(
        prompt, 1088, 1360
    )
    assert four_b._endpoint != nine_b._endpoint


def test_cloudflare_provider_sends_one_and_two_conditioned_references_with_seed() -> None:
    reference_one = ReferenceImage(filename="soft-street.png", content=make_png_bytes((511, 400)))
    reference_two = ReferenceImage(filename="otaku-dark.png", content=make_png_bytes((400, 511)))

    def handler(request: httpx.Request) -> httpx.Response:
        assert b'name="input_image_0"' in request.content
        assert b'name="input_image_1"' in request.content
        assert b'filename="soft-street.png"' in request.content
        assert b'filename="otaku-dark.png"' in request.content
        assert b'name="seed"' in request.content and b"20260826" in request.content
        return httpx.Response(
            200,
            json={"success": True, "result": {"image": "encoded-image"}},
            request=request,
        )

    provider = CloudflareWorkersAIProvider(
        make_settings(cloudflare_image_seed=20260826),
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    prompt = make_prompt().model_copy(update={"reference_images": (reference_one, reference_two)})

    assert provider.generate(prompt, 1088, 1360).image_base64 == "encoded-image"


@pytest.mark.parametrize("size", [(512, 511), (511, 512)])
def test_cloudflare_provider_rejects_oversize_conditioned_references(size: tuple[int, int]) -> None:
    provider = CloudflareWorkersAIProvider(make_settings())
    prompt = make_prompt().model_copy(
        update={
            "reference_images": (
                ReferenceImage(filename="oversize.png", content=make_png_bytes(size)),
            )
        }
    )

    with pytest.raises(ImageProviderError, match="^provider_invalid_reference_image$"):
        provider.generate(prompt, 1088, 1360)


def test_cloudflare_provider_accepts_a_data_uri_wrapped_base64_image() -> None:
    provider = CloudflareWorkersAIProvider(
        make_settings(),
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    200,
                    json={
                        "success": True,
                        "result": {"image": "data:image/jpeg;base64,encoded-image"},
                    },
                    request=request,
                )
            )
        ),
    )

    assert provider.generate(make_prompt(), 1088, 1360).image_base64 == "encoded-image"


@pytest.mark.parametrize(
    ("status_code", "message", "expected_code", "expected_retryable"),
    [
        (401, "invalid API token", "provider_invalid_credentials", False),
        (403, "permission denied", "provider_permission_denied", False),
        (404, "account not found", "provider_invalid_account_id", False),
        (429, "daily neuron quota exceeded", "provider_quota_exhausted", False),
        (429, "rate limit exceeded", "provider_rate_limit", True),
        (503, "out of capacity", "provider_out_of_capacity", True),
        (500, "internal error", "provider_server_error", True),
    ],
)
def test_cloudflare_provider_maps_api_errors_without_exposing_response_text(
    status_code: int,
    message: str,
    expected_code: str,
    expected_retryable: bool,
) -> None:
    requests = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal requests
        requests += 1
        return httpx.Response(
            status_code,
            json={"success": False, "errors": [{"message": message}]},
            request=request,
        )

    provider = CloudflareWorkersAIProvider(
        make_settings(), client=httpx.Client(transport=httpx.MockTransport(handler))
    )

    with pytest.raises(ImageProviderError, match=f"^{expected_code}$") as error:
        provider.generate(make_prompt(), 1088, 1360)

    assert error.value.retryable is expected_retryable
    assert requests == (2 if expected_retryable else 1)


def test_cloudflare_provider_retries_timeout_only_with_a_bounded_attempt_count() -> None:
    requests = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal requests
        requests += 1
        if requests == 1:
            raise httpx.ReadTimeout("timed out", request=request)
        return httpx.Response(
            200,
            json={"success": True, "result": {"image": "encoded-image"}},
            request=request,
        )

    provider = CloudflareWorkersAIProvider(
        make_settings(), client=httpx.Client(transport=httpx.MockTransport(handler))
    )

    assert provider.generate(make_prompt(), 1088, 1360).image_base64 == "encoded-image"
    assert requests == 2


@pytest.mark.parametrize(
    "response_json",
    [
        {"success": True, "result": {}},
        {"success": True, "result": {"image": 123}},
    ],
)
def test_cloudflare_provider_rejects_malformed_response(response_json: dict[str, object]) -> None:
    provider = CloudflareWorkersAIProvider(
        make_settings(),
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json=response_json, request=request)
            )
        ),
    )

    with pytest.raises(ImageProviderError, match="^provider_malformed_response$"):
        provider.generate(make_prompt(), 1088, 1360)


def test_provider_selection_defaults_to_cloudflare_and_keeps_openai_optional() -> None:
    cloudflare_settings = make_settings()
    openai_settings = make_settings(image_provider="openai")

    assert isinstance(create_image_provider(cloudflare_settings), CloudflareWorkersAIProvider)
    assert get_image_model(cloudflare_settings) == "@cf/black-forest-labs/flux-2-klein-4b"
    assert get_image_generation_size(cloudflare_settings) == "1088x1360"
    assert get_image_model(openai_settings) == "gpt-image-2"
    assert get_image_generation_size(openai_settings) == "1088x1360"


def test_cloudflare_provider_fails_fast_when_credentials_are_missing() -> None:
    with pytest.raises(ValueError, match="CLOUDFLARE_ACCOUNT_ID"):
        create_image_provider(
            Settings(
                database_url=(
                    "postgresql+psycopg://app:testing-password@localhost:5432/test_database"
                ),
                cloudflare_account_id=None,
                cloudflare_api_token=None,
            )
        )


class FakeImages:
    def __init__(self, responses: list[object]) -> None:
        self._responses = responses
        self.calls = 0
        self.last_arguments: dict[str, object] | None = None

    def generate(self, **kwargs: object) -> object:
        self.last_arguments = kwargs
        response = self._responses[self.calls]
        self.calls += 1
        if isinstance(response, Exception):
            raise response
        return response


def test_openai_provider_regression_returns_base64_and_uses_requested_size() -> None:
    images = FakeImages([SimpleNamespace(data=[SimpleNamespace(b64_json="encoded-image")])])
    provider = OpenAIImageProvider(make_settings(), client=SimpleNamespace(images=images))  # type: ignore[arg-type]

    prompt = make_prompt().model_copy(update={"flux_structured_text": '{"composition":"test"}'})

    assert provider.generate(prompt, 1088, 1360).image_base64 == "encoded-image"
    assert images.last_arguments is not None
    assert images.last_arguments["size"] == "1088x1360"
    assert images.last_arguments["prompt"] == prompt.text


def test_openai_provider_rejects_reference_conditioning_without_a_fallback() -> None:
    images = FakeImages([SimpleNamespace(data=[SimpleNamespace(b64_json="encoded-image")])])
    provider = OpenAIImageProvider(make_settings(), client=SimpleNamespace(images=images))  # type: ignore[arg-type]
    prompt = make_prompt().model_copy(
        update={
            "reference_images": (
                ReferenceImage(filename="reference.png", content=make_png_bytes((400, 400))),
            )
        }
    )

    with pytest.raises(ImageProviderError, match="^provider_reference_images_unsupported$"):
        provider.generate(prompt, 1088, 1360)
    assert images.calls == 0


def test_openai_provider_regression_retries_timeout_and_rejects_malformed_response() -> None:
    timeout_images = FakeImages(
        [TimeoutError(), SimpleNamespace(data=[SimpleNamespace(b64_json="encoded-image")])]
    )
    timeout_provider = OpenAIImageProvider(
        make_settings(), client=SimpleNamespace(images=timeout_images)
    )  # type: ignore[arg-type]
    malformed_provider = OpenAIImageProvider(
        make_settings(), client=SimpleNamespace(images=FakeImages([SimpleNamespace(data=[])]))
    )  # type: ignore[arg-type]

    assert timeout_provider.generate(make_prompt(), 1088, 1360).image_base64 == "encoded-image"
    assert timeout_images.calls == 2
    with pytest.raises(ImageProviderError, match="^malformed_response$"):
        malformed_provider.generate(make_prompt(), 1088, 1360)


def test_processor_normalizes_cloudflare_output_size_without_crop(tmp_path) -> None:
    processor = ImageProcessor(tmp_path, "1088x1360")

    processed = processor.process(
        GeneratedImagePayload(image_base64=make_encoded_png((1088, 1360))), date(2026, 8, 20)
    )

    with Image.open(processed.file_path) as image:
        assert image.size == (1080, 1350)
    assert (processed.width, processed.height) == (1080, 1350)


def test_processor_resizes_openai_payload_and_rejects_invalid_payloads(tmp_path) -> None:
    processor = ImageProcessor(tmp_path, "1088x1360")

    processed = processor.process(
        GeneratedImagePayload(image_base64=make_encoded_png((1088, 1360))), date(2026, 8, 20)
    )

    assert (processed.width, processed.height) == (1080, 1350)
    with pytest.raises(ImageProcessingError, match="unexpected_image_dimensions"):
        processor.process(
            GeneratedImagePayload(image_base64=make_encoded_png((1024, 1024))),
            date(2026, 8, 20),
        )
    with pytest.raises(ImageProcessingError, match="invalid_image"):
        processor.process(GeneratedImagePayload(image_base64="not-base64"), date(2026, 8, 20))


def make_encoded_png(size: tuple[int, int]) -> str:
    buffer = BytesIO()
    Image.new("RGB", size, color="black").save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def make_png_bytes(size: tuple[int, int]) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", size, color="black").save(buffer, format="PNG")
    return buffer.getvalue()
