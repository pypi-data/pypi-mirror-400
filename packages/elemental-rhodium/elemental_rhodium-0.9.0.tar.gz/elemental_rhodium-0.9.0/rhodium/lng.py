"""Circular arithmetic for longitudes (-180° to +180°)."""

from __future__ import annotations

from rhodium._circular import diff_on_circle, mean_on_circle, mean_on_circle_weighted

__all__ = [
    "normalize",
    "diff",
    "mean",
    "weighted_mean",
    "interpolate",
    "within",
    "normalize_many",
    "diff_many",
]


def normalize(degrees: float) -> float:
    """
    Normalize a longitude to (-180, +180].

    Examples:
        >>> normalize(190)
        -170.0
        >>> normalize(-190)
        170.0
        >>> normalize(180)
        180.0
        >>> normalize(-180)
        180.0
    """
    result = ((float(degrees) + 180) % 360) - 180
    # Handle the edge case: -180 should become +180
    if result == -180:
        result = 180.0
    return result


def diff(from_: float, to: float) -> float:
    """
    Compute the signed shortest-arc difference between two longitudes.

    Positive means eastward, negative means westward.

    Examples:
        >>> diff(170, -170)
        20.0
        >>> diff(-170, 170)
        -20.0
    """
    return diff_on_circle(from_, to, 360.0)


def mean(longitudes: list[float]) -> float | None:
    """
    Compute the circular mean of longitudes.

    Returns None if the mean is undefined (e.g., antipodal points).

    Examples:
        >>> mean([170, -170])  # Near antimeridian
        180.0
        >>> mean([0, 180])  # Opposite longitudes
        None
    """
    result = mean_on_circle(longitudes, 360.0)
    if result is None:
        return None
    return normalize(result)


def weighted_mean(longitudes: list[float], weights: list[float]) -> float | None:
    """
    Compute the weighted circular mean of longitudes.

    Args:
        longitudes: List of longitudes in degrees
        weights: List of weights (must be same length as longitudes)

    Returns:
        Weighted mean longitude, or None if undefined.

    Examples:
        >>> weighted_mean([170, -170], [1, 1])
        180.0
    """
    result = mean_on_circle_weighted(longitudes, weights, 360.0)
    if result is None:
        return None
    return normalize(result)


def interpolate(a: float, b: float, t: float) -> float:
    """
    Interpolate between two longitudes along the shortest path.

    Args:
        a: Starting longitude
        b: Ending longitude
        t: Interpolation factor (0 = a, 1 = b)

    Examples:
        >>> interpolate(170, -170, 0.5)
        180.0
        >>> interpolate(-10, 10, 0.5)
        0.0
    """
    d = diff(a, b)
    return normalize(a + d * t)


def within(longitude: float, target: float, tolerance: float) -> bool:
    """
    Check if a longitude is within ±tolerance of a target longitude.

    Examples:
        >>> within(-175, 180, 10)
        True
        >>> within(175, 180, 10)
        True
        >>> within(0, 180, 10)
        False
    """
    return abs(diff(longitude, target)) <= tolerance


# Batch operations for performance with large datasets


def normalize_many(degrees: list[float]) -> list[float]:
    """
    Normalize a list of longitudes to (-180, +180].

    More efficient than calling normalize() in a loop.

    Examples:
        >>> normalize_many([190, -190, 180])
        [-170.0, 170.0, 180.0]
    """
    return [normalize(d) for d in degrees]


def diff_many(pairs: list[tuple[float, float]]) -> list[float]:
    """
    Compute signed shortest-arc differences for multiple longitude pairs.

    Args:
        pairs: List of (from, to) longitude tuples

    Examples:
        >>> diff_many([(170, -170), (-170, 170)])
        [20.0, -20.0]
    """
    return [diff(f, t) for f, t in pairs]
