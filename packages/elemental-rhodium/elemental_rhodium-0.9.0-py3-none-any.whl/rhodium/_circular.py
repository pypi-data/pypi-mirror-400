"""Shared helper for circular arithmetic."""

from __future__ import annotations

import math


def diff_on_circle(from_: float, to: float, period: float) -> float:
    """
    Compute the signed shortest-arc difference on a circle.

    Args:
        from_: Starting angle
        to: Ending angle
        period: The period of the circle (e.g., 360 for degrees)

    Returns:
        Signed difference in the range [-period/2, +period/2]
    """
    half = period / 2
    raw = (to - from_) % period
    if raw > half:
        raw -= period
    return raw


def mean_on_circle(angles: list[float], period: float) -> float | None:
    """
    Compute the circular mean of angles.

    Args:
        angles: List of angles
        period: The period of the circle (e.g., 360 for degrees)

    Returns:
        The circular mean, or None if undefined (e.g., opposite angles)
    """
    if not angles:
        return None

    # Convert to radians for trig functions
    scale = 2 * math.pi / period
    sum_sin = sum(math.sin(a * scale) for a in angles)
    sum_cos = sum(math.cos(a * scale) for a in angles)

    # Check if the mean is undefined (vectors cancel out)
    magnitude = math.sqrt(sum_sin**2 + sum_cos**2)
    if magnitude < 1e-10:
        return None

    # Convert back from radians
    return math.atan2(sum_sin, sum_cos) / scale


def mean_on_circle_weighted(
    angles: list[float], weights: list[float], period: float
) -> float | None:
    """
    Compute the weighted circular mean of angles.
    """
    if not angles:
        return None
    if len(angles) != len(weights):
        raise ValueError("angles and weights must have the same length")

    scale = 2 * math.pi / period
    sum_sin = sum(w * math.sin(a * scale) for a, w in zip(angles, weights))
    sum_cos = sum(w * math.cos(a * scale) for a, w in zip(angles, weights))

    magnitude = math.sqrt(sum_sin**2 + sum_cos**2)
    if magnitude < 1e-10:
        return None

    return math.atan2(sum_sin, sum_cos) / scale
