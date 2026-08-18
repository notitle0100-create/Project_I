from __future__ import annotations

from datetime import UTC, date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

SEOUL_TIMEZONE = "Asia/Seoul"
LAYERING_TEMPERATURE_RANGE_THRESHOLD_C = 10.0
RAIN_SENSITIVE_PROBABILITY_THRESHOLD = 40.0


class TemperatureBand(StrEnum):
    VERY_HOT = "very_hot"
    WARM = "warm"
    MILD = "mild"
    COOL = "cool"
    CHILLY = "chilly"
    COLD = "cold"
    VERY_COLD = "very_cold"
    FREEZING = "freezing"


class WeatherCondition(StrEnum):
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    FOG = "fog"
    DRIZZLE = "drizzle"
    RAIN = "rain"
    SNOW = "snow"
    THUNDERSTORM = "thunderstorm"


class WeatherSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)

    target_date: date
    timezone: str = SEOUL_TIMEZONE
    weather_condition: WeatherCondition
    high_temperature_c: float = Field(ge=-100, le=100)
    low_temperature_c: float = Field(ge=-100, le=100)
    precipitation_probability: float = Field(ge=0, le=100)
    fetched_at: datetime

    @model_validator(mode="after")
    def validate_snapshot(self) -> WeatherSnapshot:
        if self.timezone != SEOUL_TIMEZONE:
            raise ValueError(f"timezone must be {SEOUL_TIMEZONE}")
        if self.high_temperature_c < self.low_temperature_c:
            raise ValueError(
                "high_temperature_c must be greater than or equal to low_temperature_c"
            )
        if self.fetched_at.tzinfo is None or self.fetched_at.utcoffset() is None:
            raise ValueError("fetched_at must be timezone-aware")
        return self

    @computed_field
    @property
    def temperature_range_c(self) -> float:
        return round(self.high_temperature_c - self.low_temperature_c, 1)


class StylingHints(BaseModel):
    model_config = ConfigDict(frozen=True)

    temperature_band: TemperatureBand
    layering_recommended: bool
    rain_sensitive: bool


def get_temperature_band(high_temperature_c: float) -> TemperatureBand:
    if high_temperature_c >= 28:
        return TemperatureBand.VERY_HOT
    if high_temperature_c >= 23:
        return TemperatureBand.WARM
    if high_temperature_c >= 20:
        return TemperatureBand.MILD
    if high_temperature_c >= 17:
        return TemperatureBand.COOL
    if high_temperature_c >= 12:
        return TemperatureBand.CHILLY
    if high_temperature_c >= 9:
        return TemperatureBand.COLD
    if high_temperature_c >= 5:
        return TemperatureBand.VERY_COLD
    return TemperatureBand.FREEZING


def get_styling_hints(snapshot: WeatherSnapshot) -> StylingHints:
    return StylingHints(
        temperature_band=get_temperature_band(snapshot.high_temperature_c),
        layering_recommended=(
            snapshot.temperature_range_c >= LAYERING_TEMPERATURE_RANGE_THRESHOLD_C
        ),
        rain_sensitive=(snapshot.precipitation_probability >= RAIN_SENSITIVE_PROBABILITY_THRESHOLD),
    )


def utc_now() -> datetime:
    return datetime.now(UTC)
