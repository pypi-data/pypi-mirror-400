"""Circular arithmetic for compass bearings (0° to 360°)."""

from __future__ import annotations

from rhodium._circular import diff_on_circle, mean_on_circle, mean_on_circle_weighted

__all__ = [
    "normalize",
    "diff",
    "mean",
    "weighted_mean",
    "interpolate",
    "within",
    "opposite",
    "reciprocal",
    "normalize_many",
    "diff_many",
]


def normalize(degrees: float) -> float:
    """
    Normalize a bearing to [0, 360).

    Examples:
        >>> normalize(710)
        350.0
        >>> normalize(-10)
        350.0
        >>> normalize(360)
        0.0
    """
    result = float(degrees) % 360
    # Handle floating-point edge case where tiny negatives yield 360.0
    if result >= 360:
        return 0.0
    return result


def diff(from_: float, to: float) -> float:
    """
    Compute the signed shortest-arc difference between two bearings.

    Returns a value in [-180, +180]. Positive means clockwise.

    Examples:
        >>> diff(350, 10)
        20.0
        >>> diff(10, 350)
        -20.0
        >>> diff(0, 180)
        180.0
    """
    return diff_on_circle(from_, to, 360.0)


def mean(angles: list[float]) -> float | None:
    """
    Compute the circular mean of bearings.

    Returns None if the mean is undefined (e.g., opposite directions).

    Examples:
        >>> mean([350, 10])  # Around north
        0.0
        >>> mean([0, 180])  # Opposite directions
        None
    """
    result = mean_on_circle(angles, 360.0)
    if result is None:
        return None
    # Normalize to [0, 360)
    return normalize(result)


def weighted_mean(angles: list[float], weights: list[float]) -> float | None:
    """
    Compute the weighted circular mean of bearings.

    Args:
        angles: List of bearings in degrees
        weights: List of weights (must be same length as angles)

    Returns:
        Weighted mean bearing, or None if undefined.

    Examples:
        >>> weighted_mean([0, 90], [3, 1])  # Strong pull towards 0
        22.5
    """
    result = mean_on_circle_weighted(angles, weights, 360.0)
    if result is None:
        return None
    return normalize(result)


def interpolate(a: float, b: float, t: float) -> float:
    """
    Interpolate between two bearings along the shortest arc.

    Args:
        a: Starting bearing
        b: Ending bearing
        t: Interpolation factor (0 = a, 1 = b)

    Examples:
        >>> interpolate(350, 20, 0.5)
        5.0
        >>> interpolate(10, 350, 0.5)
        0.0
    """
    d = diff(a, b)
    return normalize(a + d * t)


def within(angle: float, target: float, tolerance: float) -> bool:
    """
    Check if an angle is within ±tolerance of a target bearing.

    Examples:
        >>> within(5, 0, 10)
        True
        >>> within(355, 0, 10)
        True
        >>> within(20, 0, 10)
        False
    """
    return abs(diff(angle, target)) <= tolerance


def opposite(bearing: float) -> float:
    """
    Return the opposite bearing (180° from the given bearing).

    Also known as the reciprocal or back bearing.

    Examples:
        >>> opposite(0)
        180.0
        >>> opposite(90)
        270.0
        >>> opposite(270)
        90.0
        >>> opposite(350)
        170.0
    """
    return normalize(bearing + 180)


# Alias for opposite
reciprocal = opposite


# Batch operations for performance with large datasets


def normalize_many(degrees: list[float]) -> list[float]:
    """
    Normalize a list of bearings to [0, 360).

    More efficient than calling normalize() in a loop.

    Examples:
        >>> normalize_many([710, -10, 360])
        [350.0, 350.0, 0.0]
    """
    return [normalize(d) for d in degrees]


def diff_many(pairs: list[tuple[float, float]]) -> list[float]:
    """
    Compute signed shortest-arc differences for multiple bearing pairs.

    Args:
        pairs: List of (from, to) bearing tuples

    Examples:
        >>> diff_many([(350, 10), (10, 350)])
        [20.0, -20.0]
    """
    return [diff(f, t) for f, t in pairs]
