"""Latitude operations (-90° to +90°).

Unlike longitude and bearing, latitude does not wrap — it clamps at the poles.
This module provides utilities for clamping, validation, and common operations.
"""

from __future__ import annotations

from rhodium._validation import validate_latitude as _validate_lat
from rhodium._exceptions import InvalidLatitudeError

__all__ = [
    "clamp",
    "is_valid",
    "validate",
    "midpoint",
    "within",
    "clamp_many",
]


def clamp(degrees: float) -> float:
    """
    Clamp a latitude to [-90, 90].

    Values outside this range are clamped to the nearest pole.

    Examples:
        >>> clamp(95)
        90.0
        >>> clamp(-100)
        -90.0
        >>> clamp(45)
        45.0
    """
    if degrees > 90:
        return 90.0
    if degrees < -90:
        return -90.0
    return float(degrees)


def is_valid(degrees: float) -> bool:
    """
    Check if a latitude value is valid.

    A latitude is valid if it is:
    - Finite (not NaN or infinite)
    - Within [-90, 90]

    Examples:
        >>> is_valid(45)
        True
        >>> is_valid(91)
        False
        >>> is_valid(float('nan'))
        False
    """
    import math

    if math.isnan(degrees) or math.isinf(degrees):
        return False
    return -90 <= degrees <= 90


def validate(degrees: float, name: str = "latitude") -> None:
    """
    Validate that a latitude is finite and within [-90, 90].

    Raises:
        InvalidLatitudeError: If the latitude is invalid.

    Examples:
        >>> validate(45)  # No error
        >>> validate(91)  # Raises InvalidLatitudeError
    """
    _validate_lat(degrees, name)


def midpoint(a: float, b: float) -> float:
    """
    Calculate the midpoint between two latitudes.

    Unlike longitude, latitude midpoint is simple arithmetic since
    there's no wraparound.

    Examples:
        >>> midpoint(0, 90)
        45.0
        >>> midpoint(-45, 45)
        0.0
    """
    return (a + b) / 2


def within(latitude: float, target: float, tolerance: float) -> bool:
    """
    Check if a latitude is within ±tolerance of a target latitude.

    Examples:
        >>> within(44, 45, 2)
        True
        >>> within(40, 45, 2)
        False
    """
    return abs(latitude - target) <= tolerance


def clamp_many(degrees_list: list[float]) -> list[float]:
    """
    Clamp a list of latitudes to [-90, 90].

    Examples:
        >>> clamp_many([95, -100, 45])
        [90.0, -90.0, 45.0]
    """
    return [clamp(d) for d in degrees_list]


def hemisphere(degrees: float) -> str:
    """
    Return the hemisphere for a latitude.

    Returns:
        'N' for northern hemisphere (>= 0)
        'S' for southern hemisphere (< 0)

    Examples:
        >>> hemisphere(45)
        'N'
        >>> hemisphere(-45)
        'S'
        >>> hemisphere(0)
        'N'
    """
    return "N" if degrees >= 0 else "S"
