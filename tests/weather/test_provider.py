from __future__ import annotations

from datetime import date

import httpx
import pytest

from seoul_mens_daily_edit.weather.domain import WeatherCondition
from seoul_mens_daily_edit.weather.provider import (
    OpenMeteoWeatherProvider,
    WeatherProviderError,
    WeatherProviderResponseError,
    WeatherProviderTimeoutError,
)


def forecast_payload(target_date: date, **daily_overrides: object) -> dict[str, object]:
    daily: dict[str, object] = {
        "time": [target_date.isoformat()],
        "temperature_2m_max": [25.3],
        "temperature_2m_min": [14.6],
        "precipitation_probability_max": [45],
        "weather_code": [63],
    }
    daily.update(daily_overrides)
    return {"timezone": "Asia/Seoul", "daily": daily}


def build_provider(
    handler: httpx.MockTransport.Handler, *, max_retries: int = 0
) -> OpenMeteoWeatherProvider:
    return OpenMeteoWeatherProvider(
        max_retries=max_retries,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def test_normalizes_open_meteo_daily_forecast() -> None:
    target_date = date(2026, 8, 20)

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.scheme == "https"
        assert request.url.host == "api.open-meteo.com"
        assert request.url.params["timezone"] == "Asia/Seoul"
        assert request.url.params["start_date"] == target_date.isoformat()
        return httpx.Response(200, json=forecast_payload(target_date))

    snapshot = build_provider(handler).fetch_daily_forecast(target_date)

    assert snapshot.target_date == target_date
    assert snapshot.weather_condition == WeatherCondition.RAIN
    assert snapshot.high_temperature_c == 25.3
    assert snapshot.low_temperature_c == 14.6
    assert snapshot.temperature_range_c == 10.7
    assert snapshot.precipitation_probability == 45.0
    assert snapshot.fetched_at.tzinfo is not None


def test_provider_timeout_is_explicit() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    with pytest.raises(WeatherProviderTimeoutError, match="timed out"):
        build_provider(handler).fetch_daily_forecast(date(2026, 8, 20))


def test_provider_error_response_is_explicit() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    with pytest.raises(WeatherProviderError, match="HTTP 503"):
        build_provider(handler).fetch_daily_forecast(date(2026, 8, 20))


def test_provider_rejects_invalid_json() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not-json")

    with pytest.raises(WeatherProviderResponseError, match="invalid JSON"):
        build_provider(handler).fetch_daily_forecast(date(2026, 8, 20))


@pytest.mark.parametrize(
    "payload",
    [
        {"timezone": "Asia/Seoul", "daily": {"time": ["2026-08-20"]}},
        {"timezone": "UTC", "daily": {}},
        {"timezone": "Asia/Seoul", "daily": {"time": ["2026-08-21"]}},
    ],
)
def test_provider_rejects_malformed_or_missing_forecast(payload: dict[str, object]) -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    with pytest.raises(WeatherProviderResponseError):
        build_provider(handler).fetch_daily_forecast(date(2026, 8, 20))
