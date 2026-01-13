"""Rhodium: Circular arithmetic for geographic coordinates."""

from rhodium import bearing, bbox, lat, lng
from rhodium.bbox import BBox, Point
from rhodium._exceptions import (
    RhodiumError,
    InvalidCoordinateError,
    InvalidLatitudeError,
    InvalidLongitudeError,
    InvalidBearingError,
    InvalidBBoxError,
    EmptyInputError,
)

__version__ = "0.9.0"
__all__ = [
    "bearing",
    "lat",
    "lng",
    "bbox",
    "BBox",
    "Point",
    # Exceptions
    "RhodiumError",
    "InvalidCoordinateError",
    "InvalidLatitudeError",
    "InvalidLongitudeError",
    "InvalidBearingError",
    "InvalidBBoxError",
    "EmptyInputError",
]
