from __future__ import annotations

import json
import re
from io import BytesIO
from typing import Protocol

import httpx
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)
from PIL import Image, UnidentifiedImageError

from seoul_mens_daily_edit.core.config import Settings
from seoul_mens_daily_edit.images.domain import (
    GeneratedImagePayload,
    ImageGenerationPrompt,
    ReferenceImage,
)

MAX_PROVIDER_ATTEMPTS = 2
MAX_REFERENCE_IMAGES = 2
MAX_REFERENCE_DIMENSION = 511
_CLOUDFLARE_ACCOUNT_ID_PATTERN = re.compile(r"^[a-f0-9]{32}$", re.IGNORECASE)
_CLOUDFLARE_MODEL_PATTERN = re.compile(r"^@cf/[a-z0-9-]+/[a-z0-9.-]+$", re.IGNORECASE)


class ImageProvider(Protocol):
    def generate(
        self, prompt: ImageGenerationPrompt, width: int, height: int
    ) -> GeneratedImagePayload: ...


class ImageProviderError(RuntimeError):
    def __init__(self, code: str, *, retryable: bool) -> None:
        super().__init__(code)
        self.code = code
        self.retryable = retryable


class CloudflareWorkersAIProvider:
    """Cloudflare Workers AI REST adapter for the configured image model only."""

    def __init__(self, settings: Settings, *, client: httpx.Client | None = None) -> None:
        account_id = settings.cloudflare_account_id
        api_token = (
            settings.cloudflare_api_token.get_secret_value()
            if settings.cloudflare_api_token is not None
            else None
        )
        if not account_id or not api_token:
            raise ValueError(
                "CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN are required "
                "for Cloudflare image generation"
            )
        if not _CLOUDFLARE_ACCOUNT_ID_PATTERN.fullmatch(account_id):
            raise ValueError("CLOUDFLARE_ACCOUNT_ID must be a 32-character account identifier")
        if not _CLOUDFLARE_MODEL_PATTERN.fullmatch(settings.cloudflare_image_model):
            raise ValueError("CLOUDFLARE_IMAGE_MODEL must be a supported @cf model identifier")

        self._account_id = account_id
        self._api_token = api_token
        self._model = settings.cloudflare_image_model
        self._guidance = settings.cloudflare_image_guidance
        self._seed = settings.cloudflare_image_seed
        self._client = client or httpx.Client(timeout=settings.cloudflare_image_timeout_seconds)

    def generate(
        self, prompt: ImageGenerationPrompt, width: int, height: int
    ) -> GeneratedImagePayload:
        _validate_cloudflare_dimensions(width, height)
        last_error: ImageProviderError | None = None
        for attempt in range(MAX_PROVIDER_ATTEMPTS):
            cause: Exception
            try:
                response = self._client.post(
                    self._endpoint,
                    headers={"Authorization": f"Bearer {self._api_token}"},
                    files=self._multipart_fields(prompt, width, height),
                )
                payload = _decode_cloudflare_response(response)
                return payload
            except httpx.TimeoutException as exc:
                cause = exc
                error = ImageProviderError("provider_timeout", retryable=True)
            except httpx.TransportError as exc:
                cause = exc
                error = ImageProviderError("provider_unavailable", retryable=True)
            except ImageProviderError as exc:
                cause = exc
                error = exc
            last_error = error
            if not error.retryable or attempt + 1 == MAX_PROVIDER_ATTEMPTS:
                raise error from cause
        if last_error is None:
            raise ImageProviderError("provider_unavailable", retryable=False)
        raise last_error

    @property
    def _endpoint(self) -> str:
        return (
            f"https://api.cloudflare.com/client/v4/accounts/{self._account_id}/ai/run/{self._model}"
        )

    def _multipart_fields(
        self, prompt: ImageGenerationPrompt, width: int, height: int
    ) -> dict[str, tuple[None, str] | tuple[str, bytes, str]]:
        fields: dict[str, tuple[None, str] | tuple[str, bytes, str]] = {
            "prompt": (None, prompt.flux_structured_text or prompt.text),
            "width": (None, str(width)),
            "height": (None, str(height)),
        }
        if self._guidance is not None:
            fields["guidance"] = (None, str(self._guidance))
        if self._seed is not None:
            fields["seed"] = (None, str(self._seed))
        if len(prompt.reference_images) > MAX_REFERENCE_IMAGES:
            raise ImageProviderError("provider_invalid_reference_image", retryable=False)
        for index, reference in enumerate(prompt.reference_images):
            _validate_reference_image(reference)
            fields[f"input_image_{index}"] = (
                reference.filename,
                reference.content,
                "image/png",
            )
        return fields


class OpenAIImageProvider:
    """Optional provider retained for explicit IMAGE_PROVIDER=openai selection."""

    def __init__(self, settings: Settings, *, client: OpenAI | None = None) -> None:
        api_key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else None
        if not api_key and client is None:
            raise ValueError("OPENAI_API_KEY is required for OpenAI image generation")
        self._model = settings.openai_image_model
        self._quality = settings.openai_image_quality
        self._client = client or OpenAI(
            api_key=api_key,
            timeout=settings.openai_image_timeout_seconds,
            max_retries=0,
        )

    def generate(
        self, prompt: ImageGenerationPrompt, width: int, height: int
    ) -> GeneratedImagePayload:
        if prompt.reference_images:
            raise ImageProviderError("provider_reference_images_unsupported", retryable=False)
        last_error: ImageProviderError | None = None
        for attempt in range(MAX_PROVIDER_ATTEMPTS):
            try:
                response = self._client.images.generate(
                    model=self._model,
                    prompt=prompt.text,
                    size=f"{width}x{height}",
                    quality=self._quality,
                    n=1,
                )
                return GeneratedImagePayload(image_base64=_extract_openai_base64(response))
            except (
                APIConnectionError,
                APIStatusError,
                APITimeoutError,
                AuthenticationError,
                ImageProviderError,
                RateLimitError,
                TimeoutError,
            ) as exc:
                error = _map_openai_error(exc)
                last_error = error
                if not error.retryable or attempt + 1 == MAX_PROVIDER_ATTEMPTS:
                    raise error from exc
        if last_error is None:
            raise ImageProviderError("provider_error", retryable=False)
        raise last_error


def create_image_provider(settings: Settings) -> ImageProvider:
    if settings.image_provider == "cloudflare":
        return CloudflareWorkersAIProvider(settings)
    return OpenAIImageProvider(settings)


def get_image_model(settings: Settings) -> str:
    if settings.image_provider == "cloudflare":
        return settings.cloudflare_image_model
    return settings.openai_image_model


def get_image_generation_size(settings: Settings) -> str:
    if settings.image_provider == "cloudflare":
        return settings.cloudflare_image_size
    return settings.openai_image_size


def _validate_cloudflare_dimensions(width: int, height: int) -> None:
    if not 256 <= width <= 1920 or not 256 <= height <= 1920:
        raise ImageProviderError("provider_invalid_request", retryable=False)


def _validate_reference_image(reference: ReferenceImage) -> None:
    try:
        with Image.open(BytesIO(reference.content)) as image:
            image.load()
            if (
                image.format != "PNG"
                or image.width > MAX_REFERENCE_DIMENSION
                or image.height > MAX_REFERENCE_DIMENSION
            ):
                raise ImageProviderError("provider_invalid_reference_image", retryable=False)
    except ImageProviderError:
        raise
    except (UnidentifiedImageError, OSError) as exc:
        raise ImageProviderError("provider_invalid_reference_image", retryable=False) from exc


def _decode_cloudflare_response(response: httpx.Response) -> GeneratedImagePayload:
    try:
        response_data = response.json()
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ImageProviderError("provider_malformed_response", retryable=False) from exc
    if not isinstance(response_data, dict):
        raise ImageProviderError("provider_malformed_response", retryable=False)
    if response.is_error or response_data.get("success") is not True:
        raise _map_cloudflare_error(response.status_code, response_data)
    result = response_data.get("result")
    image_base64 = result.get("image") if isinstance(result, dict) else None
    if not isinstance(image_base64, str) or not image_base64:
        raise ImageProviderError("provider_malformed_response", retryable=False)
    return GeneratedImagePayload(image_base64=_strip_data_uri_prefix(image_base64))


def _map_cloudflare_error(
    status_code: int, response_data: dict[object, object]
) -> ImageProviderError:
    message = _cloudflare_error_text(response_data)
    normalized_message = message.lower()
    if status_code == 401:
        return ImageProviderError("provider_invalid_credentials", retryable=False)
    if status_code == 404:
        return ImageProviderError("provider_invalid_account_id", retryable=False)
    if status_code == 403:
        return ImageProviderError("provider_permission_denied", retryable=False)
    if "quota" in normalized_message or "neurons" in normalized_message:
        return ImageProviderError("provider_quota_exhausted", retryable=False)
    if status_code == 429:
        return ImageProviderError("provider_rate_limit", retryable=True)
    if "out of capacity" in normalized_message or "capacity" in normalized_message:
        return ImageProviderError("provider_out_of_capacity", retryable=True)
    if 500 <= status_code <= 599:
        return ImageProviderError("provider_server_error", retryable=True)
    if 400 <= status_code <= 499:
        return ImageProviderError("provider_invalid_request", retryable=False)
    return ImageProviderError("provider_malformed_response", retryable=False)


def _cloudflare_error_text(response_data: dict[object, object]) -> str:
    errors = response_data.get("errors")
    if not isinstance(errors, list):
        return ""
    messages = [error.get("message", "") for error in errors if isinstance(error, dict)]
    return " ".join(message for message in messages if isinstance(message, str))


def _strip_data_uri_prefix(image_base64: str) -> str:
    if image_base64.startswith("data:image/"):
        _, separator, encoded_image = image_base64.partition(",")
        if separator != "," or not encoded_image:
            raise ImageProviderError("provider_malformed_response", retryable=False)
        return encoded_image
    return image_base64


def _extract_openai_base64(response: object) -> str:
    data = getattr(response, "data", None)
    if not isinstance(data, list) or not data:
        raise ImageProviderError("malformed_response", retryable=False)
    encoded_image = getattr(data[0], "b64_json", None)
    if not isinstance(encoded_image, str) or not encoded_image:
        raise ImageProviderError("malformed_response", retryable=False)
    return encoded_image


def _map_openai_error(exc: Exception) -> ImageProviderError:
    if isinstance(exc, (APITimeoutError, TimeoutError, APIConnectionError)):
        return ImageProviderError("provider_timeout", retryable=True)
    if isinstance(exc, AuthenticationError):
        return ImageProviderError("provider_authentication", retryable=False)
    if isinstance(exc, RateLimitError):
        return ImageProviderError("provider_rate_limit", retryable=True)
    if isinstance(exc, APIStatusError):
        return ImageProviderError("provider_error", retryable=exc.status_code >= 500)
    if isinstance(exc, ImageProviderError):
        return exc
    return ImageProviderError("provider_error", retryable=False)
