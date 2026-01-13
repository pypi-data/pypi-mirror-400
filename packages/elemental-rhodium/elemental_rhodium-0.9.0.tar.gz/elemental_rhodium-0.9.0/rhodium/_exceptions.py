"""Exception hierarchy for rhodium."""

from __future__ import annotations


class RhodiumError(ValueError):
    """Base exception for all rhodium errors."""

    pass


class InvalidCoordinateError(RhodiumError):
    """Base class for invalid coordinate errors."""

    pass


class InvalidLatitudeError(InvalidCoordinateError):
    """Raised when a latitude value is invalid."""

    def __init__(self, value: float, name: str = "latitude", reason: str | None = None):
        self.value = value
        self.name = name
        if reason:
            message = f"{name}: {reason}"
        else:
            message = f"{name} must be between -90 and 90, got {value}"
        super().__init__(message)


class InvalidLongitudeError(InvalidCoordinateError):
    """Raised when a longitude value is invalid (NaN or infinite)."""

    def __init__(self, value: float, name: str = "longitude", reason: str | None = None):
        self.value = value
        self.name = name
        if reason:
            message = f"{name}: {reason}"
        else:
            message = f"{name} is invalid: {value}"
        super().__init__(message)


class InvalidBearingError(InvalidCoordinateError):
    """Raised when a bearing value is invalid (NaN or infinite)."""

    def __init__(self, value: float, name: str = "bearing", reason: str | None = None):
        self.value = value
        self.name = name
        if reason:
            message = f"{name}: {reason}"
        else:
            message = f"{name} is invalid: {value}"
        super().__init__(message)


class InvalidBBoxError(RhodiumError):
    """Raised when a bounding box is invalid."""

    def __init__(self, message: str):
        super().__init__(message)


class EmptyInputError(RhodiumError):
    """Raised when an operation requires non-empty input."""

    def __init__(self, message: str = "Input cannot be empty"):
        super().__init__(message)
