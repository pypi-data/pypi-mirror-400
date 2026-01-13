"""Tests for the exception hierarchy."""

import pytest

from rhodium import (
    RhodiumError,
    InvalidCoordinateError,
    InvalidLatitudeError,
    InvalidLongitudeError,
    InvalidBearingError,
    InvalidBBoxError,
    EmptyInputError,
)
from rhodium import bbox, lat
from rhodium.bbox import Point


class TestExceptionHierarchy:
    def test_rhodium_error_is_value_error(self):
        """RhodiumError should be a subclass of ValueError for backwards compatibility."""
        assert issubclass(RhodiumError, ValueError)

    def test_invalid_coordinate_is_rhodium_error(self):
        assert issubclass(InvalidCoordinateError, RhodiumError)

    def test_specific_errors_are_coordinate_errors(self):
        assert issubclass(InvalidLatitudeError, InvalidCoordinateError)
        assert issubclass(InvalidLongitudeError, InvalidCoordinateError)
        assert issubclass(InvalidBearingError, InvalidCoordinateError)

    def test_bbox_error_is_rhodium_error(self):
        assert issubclass(InvalidBBoxError, RhodiumError)

    def test_empty_input_is_rhodium_error(self):
        assert issubclass(EmptyInputError, RhodiumError)


class TestInvalidLatitudeError:
    def test_error_contains_value(self):
        error = InvalidLatitudeError(91, "test_lat")
        assert error.value == 91
        assert error.name == "test_lat"
        assert "91" in str(error)

    def test_error_with_custom_reason(self):
        error = InvalidLatitudeError(float('nan'), "lat", reason="cannot be NaN")
        assert "cannot be NaN" in str(error)

    def test_raised_by_validation(self):
        with pytest.raises(InvalidLatitudeError) as exc_info:
            lat.validate(100)
        assert exc_info.value.value == 100


class TestInvalidLongitudeError:
    def test_error_contains_value(self):
        error = InvalidLongitudeError(float('nan'), "test_lng")
        assert error.name == "test_lng"


class TestInvalidBearingError:
    def test_error_contains_value(self):
        error = InvalidBearingError(float('inf'), "heading")
        assert error.name == "heading"


class TestInvalidBBoxError:
    def test_error_message(self):
        error = InvalidBBoxError("south > north")
        assert "south > north" in str(error)

    def test_raised_by_create(self):
        with pytest.raises(InvalidBBoxError):
            bbox.create(
                Point(lng=0, lat=50),  # south = 50
                Point(lng=10, lat=40),  # north = 40
            )


class TestEmptyInputError:
    def test_default_message(self):
        error = EmptyInputError()
        assert "empty" in str(error).lower()

    def test_custom_message(self):
        error = EmptyInputError("points list is empty")
        assert "points list is empty" in str(error)

    def test_raised_by_from_points(self):
        with pytest.raises(EmptyInputError):
            bbox.from_points([])


class TestCatchingErrors:
    def test_catch_specific_error(self):
        """Test that specific errors can be caught."""
        caught = False
        try:
            lat.validate(100)
        except InvalidLatitudeError:
            caught = True
        assert caught

    def test_catch_base_error(self):
        """Test that base RhodiumError catches all rhodium errors."""
        caught = False
        try:
            lat.validate(100)
        except RhodiumError:
            caught = True
        assert caught

    def test_catch_as_value_error(self):
        """Test that errors can still be caught as ValueError."""
        caught = False
        try:
            lat.validate(100)
        except ValueError:
            caught = True
        assert caught
