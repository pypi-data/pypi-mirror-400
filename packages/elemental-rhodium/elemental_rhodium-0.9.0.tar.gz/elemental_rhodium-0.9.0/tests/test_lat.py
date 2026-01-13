"""Tests for the lat module."""

import math
import pytest

from rhodium import lat
from rhodium._exceptions import InvalidLatitudeError


class TestClamp:
    def test_within_range(self):
        assert lat.clamp(45) == 45.0
        assert lat.clamp(0) == 0.0
        assert lat.clamp(-45) == -45.0

    def test_at_boundaries(self):
        assert lat.clamp(90) == 90.0
        assert lat.clamp(-90) == -90.0

    def test_above_max(self):
        assert lat.clamp(95) == 90.0
        assert lat.clamp(100) == 90.0
        assert lat.clamp(180) == 90.0

    def test_below_min(self):
        assert lat.clamp(-95) == -90.0
        assert lat.clamp(-100) == -90.0
        assert lat.clamp(-180) == -90.0


class TestIsValid:
    def test_valid_latitudes(self):
        assert lat.is_valid(0) is True
        assert lat.is_valid(45) is True
        assert lat.is_valid(-45) is True
        assert lat.is_valid(90) is True
        assert lat.is_valid(-90) is True

    def test_invalid_out_of_range(self):
        assert lat.is_valid(91) is False
        assert lat.is_valid(-91) is False
        assert lat.is_valid(180) is False

    def test_invalid_nan(self):
        assert lat.is_valid(float('nan')) is False

    def test_invalid_inf(self):
        assert lat.is_valid(float('inf')) is False
        assert lat.is_valid(float('-inf')) is False


class TestValidate:
    def test_valid_latitude(self):
        # Should not raise
        lat.validate(45)
        lat.validate(0)
        lat.validate(90)
        lat.validate(-90)

    def test_invalid_out_of_range(self):
        with pytest.raises(InvalidLatitudeError):
            lat.validate(91)

    def test_invalid_nan(self):
        with pytest.raises(InvalidLatitudeError):
            lat.validate(float('nan'))

    def test_invalid_inf(self):
        with pytest.raises(InvalidLatitudeError):
            lat.validate(float('inf'))

    def test_exception_contains_value(self):
        try:
            lat.validate(100)
        except InvalidLatitudeError as e:
            assert e.value == 100


class TestMidpoint:
    def test_simple_midpoint(self):
        assert lat.midpoint(0, 90) == 45.0
        assert lat.midpoint(-90, 90) == 0.0
        assert lat.midpoint(0, 0) == 0.0

    def test_negative_midpoint(self):
        assert lat.midpoint(-45, 45) == 0.0
        assert lat.midpoint(-90, 0) == -45.0


class TestWithin:
    def test_within_tolerance(self):
        assert lat.within(44, 45, 2) is True
        assert lat.within(46, 45, 2) is True
        assert lat.within(45, 45, 0) is True

    def test_outside_tolerance(self):
        assert lat.within(40, 45, 2) is False
        assert lat.within(50, 45, 2) is False


class TestClampMany:
    def test_clamp_many(self):
        result = lat.clamp_many([95, -100, 45, 0, 90, -90])
        assert result == [90.0, -90.0, 45.0, 0.0, 90.0, -90.0]

    def test_empty_list(self):
        assert lat.clamp_many([]) == []


class TestHemisphere:
    def test_northern(self):
        assert lat.hemisphere(45) == 'N'
        assert lat.hemisphere(90) == 'N'
        assert lat.hemisphere(0.1) == 'N'

    def test_southern(self):
        assert lat.hemisphere(-45) == 'S'
        assert lat.hemisphere(-90) == 'S'
        assert lat.hemisphere(-0.1) == 'S'

    def test_equator(self):
        # Zero is considered northern hemisphere by convention
        assert lat.hemisphere(0) == 'N'
