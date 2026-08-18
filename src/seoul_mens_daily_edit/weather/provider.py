from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any

import httpx

from seoul_mens_daily_edit.weather.domain import (
    SEOUL_TIMEZONE,
    WeatherCondition,
    WeatherSnapshot,
    utc_now,
)

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
SEOUL_LATITUDE = 37.5665
SEOUL_LONGITUDE = 126.9780


class WeatherProviderError(RuntimeError):
    """The weather provider could not supply a usable forecast."""


class WeatherProviderTimeoutError(WeatherProviderError):
    """The weather provider exceeded its configured timeout."""


class WeatherProviderResponseError(WeatherProviderError):
    """The weather provider returned malformed or incomplete data."""


class OpenMeteoWeatherProvider:
    """Single-purpose adapter for Open-Meteo's daily forecast endpoint."""

    def __init__(
        self,
        *,
        timeout_seconds: float = 5.0,
        max_retries: int = 1,
        client: httpx.Client | None = None,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        if not 0 <= max_retries <= 3:
            raise ValueError("max_retries must be between 0 and 3")

        self._max_retries = max_retries
        self._client = client or httpx.Client(
            timeout=httpx.Timeout(timeout_seconds),
            follow_redirects=False,
        )

    def fetch_daily_forecast(self, target_date: date) -> WeatherSnapshot:
        response = self._get_response(target_date)
        return _parse_daily_forecast(response, target_date)

    def _get_response(self, target_date: date) -> Mapping[str, Any]:
        parameters = {
            "latitude": SEOUL_LATITUDE,
            "longitude": SEOUL_LONGITUDE,
            "daily": (
                "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code"
            ),
            "timezone": SEOUL_TIMEZONE,
            "start_date": target_date.isoformat(),
            "end_date": target_date.isoformat(),
        }

        for attempt in range(self._max_retries + 1):
            try:
                response = self._client.get(OPEN_METEO_FORECAST_URL, params=parameters)
            except httpx.TimeoutException as error:
                if attempt < self._max_retries:
                    continue
                raise WeatherProviderTimeoutError("Open-Meteo request timed out") from error
            except httpx.HTTPError as error:
                if attempt < self._max_retries:
                    continue
                raise WeatherProviderError("Open-Meteo request failed") from error

            if response.is_error:
                if response.status_code >= 500 and attempt < self._max_retries:
                    continue
                raise WeatherProviderError(f"Open-Meteo returned HTTP {response.status_code}")

            try:
                payload = response.json()
            except ValueError as error:
                raise WeatherProviderResponseError("Open-Meteo returned invalid JSON") from error
            if not isinstance(payload, Mapping):
                raise WeatherProviderResponseError("Open-Meteo response must be an object")
            return payload

        raise AssertionError("bounded retry loop must return or raise")


def _parse_daily_forecast(payload: Mapping[str, Any], target_date: date) -> WeatherSnapshot:
    if payload.get("timezone") != SEOUL_TIMEZONE:
        raise WeatherProviderResponseError("Open-Meteo response timezone is missing or unexpected")

    daily = payload.get("daily")
    if not isinstance(daily, Mapping):
        raise WeatherProviderResponseError("Open-Meteo response is missing daily forecast data")

    target_index = _get_target_index(daily, target_date)
    high_temperature_c = _get_float(daily, "temperature_2m_max", target_index)
    low_temperature_c = _get_float(daily, "temperature_2m_min", target_index)
    precipitation_probability = _get_float(daily, "precipitation_probability_max", target_index)
    weather_code = _get_weather_code(daily, target_index)

    try:
        return WeatherSnapshot(
            target_date=target_date,
            weather_condition=_weather_condition_from_code(weather_code),
            high_temperature_c=high_temperature_c,
            low_temperature_c=low_temperature_c,
            precipitation_probability=precipitation_probability,
            fetched_at=utc_now(),
        )
    except ValueError as error:
        raise WeatherProviderResponseError("Open-Meteo forecast values are invalid") from error


def _get_target_index(daily: Mapping[str, Any], target_date: date) -> int:
    values = daily.get("time")
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise WeatherProviderResponseError("Open-Meteo response is missing daily time values")
    target = target_date.isoformat()
    try:
        return list(values).index(target)
    except ValueError as error:
        raise WeatherProviderResponseError(
            "Open-Meteo response does not contain the target date"
        ) from error


def _get_float(daily: Mapping[str, Any], name: str, index: int) -> float:
    values = daily.get(name)
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)) or index >= len(values):
        raise WeatherProviderResponseError(f"Open-Meteo response is missing {name}")
    value = values[index]
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise WeatherProviderResponseError(f"Open-Meteo response has invalid {name}")
    return float(value)


def _get_weather_code(daily: Mapping[str, Any], index: int) -> int:
    value = _get_float(daily, "weather_code", index)
    if not value.is_integer():
        raise WeatherProviderResponseError("Open-Meteo response has invalid weather_code")
    return int(value)


def _weather_condition_from_code(weather_code: int) -> WeatherCondition:
    if weather_code == 0:
        return WeatherCondition.CLEAR
    if weather_code in {1, 2}:
        return WeatherCondition.PARTLY_CLOUDY
    if weather_code == 3:
        return WeatherCondition.CLOUDY
    if weather_code in {45, 48}:
        return WeatherCondition.FOG
    if weather_code in {51, 53, 55, 56, 57}:
        return WeatherCondition.DRIZZLE
    if weather_code in {61, 63, 65, 66, 67, 80, 81, 82}:
        return WeatherCondition.RAIN
    if weather_code in {71, 73, 75, 77, 85, 86}:
        return WeatherCondition.SNOW
    if weather_code in {95, 96, 99}:
        return WeatherCondition.THUNDERSTORM
    raise WeatherProviderResponseError("Open-Meteo response has unsupported weather_code")
