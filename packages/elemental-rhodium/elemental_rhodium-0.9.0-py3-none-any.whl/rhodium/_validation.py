"""Input validation helpers."""

from __future__ import annotations

import math

from rhodium._exceptions import (
    InvalidLatitudeError,
    InvalidLongitudeError,
    InvalidBearingError,
)


def validate_finite(value: float, name: str) -> None:
    """
    Validate that a value is finite (not NaN or infinity).

    Raises:
        ValueError: If the value is NaN or infinite.
    """
    if math.isnan(value):
        raise ValueError(f"{name} cannot be NaN")
    if math.isinf(value):
        raise ValueError(f"{name} cannot be infinite")


def validate_latitude(lat: float, name: str = "latitude") -> None:
    """
    Validate that a latitude is finite and within [-90, 90].

    Raises:
        InvalidLatitudeError: If the latitude is invalid.
    """
    if math.isnan(lat):
        raise InvalidLatitudeError(lat, name, "cannot be NaN")
    if math.isinf(lat):
        raise InvalidLatitudeError(lat, name, "cannot be infinite")
    if lat < -90 or lat > 90:
        raise InvalidLatitudeError(lat, name)


def validate_longitude(lng: float, name: str = "longitude") -> None:
    """
    Validate that a longitude is finite.

    Note: Longitudes outside [-180, 180] are valid input and will be normalized.
    Only NaN and infinity are rejected.

    Raises:
        InvalidLongitudeError: If the longitude is NaN or infinite.
    """
    if math.isnan(lng):
        raise InvalidLongitudeError(lng, name, "cannot be NaN")
    if math.isinf(lng):
        raise InvalidLongitudeError(lng, name, "cannot be infinite")


def validate_bearing(bearing: float, name: str = "bearing") -> None:
    """
    Validate that a bearing is finite.

    Note: Bearings outside [0, 360) are valid input and will be normalized.
    Only NaN and infinity are rejected.

    Raises:
        InvalidBearingError: If the bearing is NaN or infinite.
    """
    if math.isnan(bearing):
        raise InvalidBearingError(bearing, name, "cannot be NaN")
    if math.isinf(bearing):
        raise InvalidBearingError(bearing, name, "cannot be infinite")
