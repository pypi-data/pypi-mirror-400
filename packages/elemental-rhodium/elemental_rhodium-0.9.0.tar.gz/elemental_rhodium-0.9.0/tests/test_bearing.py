"""Tests for rhodium.bearing module."""

import pytest

from rhodium import bearing


class TestNormalize:
    """Tests for bearing.normalize()."""

    def test_positive_overflow(self) -> None:
        assert bearing.normalize(710) == 350.0

    def test_negative_value(self) -> None:
        assert bearing.normalize(-10) == 350.0

    def test_exact_360(self) -> None:
        assert bearing.normalize(360) == 0.0

    def test_zero(self) -> None:
        assert bearing.normalize(0) == 0.0

    def test_normal_value(self) -> None:
        assert bearing.normalize(90) == 90.0

    def test_large_negative(self) -> None:
        assert bearing.normalize(-370) == 350.0

    def test_just_under_360(self) -> None:
        assert bearing.normalize(359.9) == pytest.approx(359.9)


class TestDiff:
    """Tests for bearing.diff()."""

    def test_clockwise_across_north(self) -> None:
        # 350° to 10° going clockwise is +20°
        assert bearing.diff(350, 10) == pytest.approx(20.0)

    def test_counterclockwise_across_north(self) -> None:
        # 10° to 350° going counterclockwise is -20°
        assert bearing.diff(10, 350) == pytest.approx(-20.0)

    def test_opposite_directions(self) -> None:
        # 0° to 180° is exactly 180°
        assert bearing.diff(0, 180) == pytest.approx(180.0)

    def test_same_bearing(self) -> None:
        assert bearing.diff(45, 45) == pytest.approx(0.0)

    def test_small_clockwise(self) -> None:
        assert bearing.diff(10, 20) == pytest.approx(10.0)

    def test_small_counterclockwise(self) -> None:
        assert bearing.diff(20, 10) == pytest.approx(-10.0)

    def test_179_to_181(self) -> None:
        # Should go the short way (clockwise)
        assert bearing.diff(179, 181) == pytest.approx(2.0)

    def test_181_to_179(self) -> None:
        assert bearing.diff(181, 179) == pytest.approx(-2.0)


class TestMean:
    """Tests for bearing.mean()."""

    def test_around_north(self) -> None:
        # Mean of 350° and 10° should be 0° (north)
        result = bearing.mean([350, 10])
        assert result == pytest.approx(0.0, abs=1e-9)

    def test_opposite_directions(self) -> None:
        # Mean of 0° and 180° is undefined
        assert bearing.mean([0, 180]) is None

    def test_empty_list(self) -> None:
        assert bearing.mean([]) is None

    def test_single_value(self) -> None:
        result = bearing.mean([45])
        assert result == pytest.approx(45.0)

    def test_same_values(self) -> None:
        result = bearing.mean([90, 90, 90])
        assert result == pytest.approx(90.0)

    def test_east_bearings(self) -> None:
        result = bearing.mean([80, 100])
        assert result == pytest.approx(90.0)

    def test_near_opposite(self) -> None:
        # 0° and 179° - should have a mean near 90°
        result = bearing.mean([0, 179])
        assert result is not None
        assert result == pytest.approx(89.5, abs=0.1)


class TestWeightedMean:
    """Tests for bearing.weighted_mean()."""

    def test_strong_pull(self) -> None:
        # [0, 90] with weights [3, 1] should be closer to 0
        # Expected: atan2(3*sin(0)+1*sin(90), 3*cos(0)+1*cos(90))
        # = atan2(1, 3) = 18.43 degrees
        result = bearing.weighted_mean([0, 90], [3, 1])
        assert result == pytest.approx(18.4349, abs=0.0001)

    def test_equal_weights(self) -> None:
        # Should match regular mean
        result = bearing.weighted_mean([350, 10], [1, 1])
        assert result == pytest.approx(0.0)

    def test_zero_weight_ignored(self) -> None:
        # [0, 90] with weights [1, 0] should be 0
        result = bearing.weighted_mean([0, 90], [1, 0])
        assert result == pytest.approx(0.0)

    def test_opposite_cancel(self) -> None:
        # Equal weights on opposite directions -> None
        assert bearing.weighted_mean([0, 180], [1, 1]) is None

    def test_unequal_opposite_resolves(self) -> None:
        # Unequal weights on opposite directions -> follows stronger weight
        result = bearing.weighted_mean([0, 180], [2, 1])
        assert result == pytest.approx(0.0)

    def test_length_mismatch(self) -> None:
        with pytest.raises(ValueError, match="same length"):
            bearing.weighted_mean([0, 90], [1])


class TestInterpolate:
    """Tests for bearing.interpolate()."""

    def test_across_north_midpoint(self) -> None:
        # Midpoint between 350° and 20° is 5°
        assert bearing.interpolate(350, 20, 0.5) == pytest.approx(5.0)

    def test_across_north_reverse(self) -> None:
        # Midpoint between 10° and 350° is 0°
        assert bearing.interpolate(10, 350, 0.5) == pytest.approx(0.0)

    def test_start_point(self) -> None:
        assert bearing.interpolate(100, 200, 0.0) == pytest.approx(100.0)

    def test_end_point(self) -> None:
        assert bearing.interpolate(100, 200, 1.0) == pytest.approx(200.0)

    def test_quarter_point(self) -> None:
        assert bearing.interpolate(0, 100, 0.25) == pytest.approx(25.0)

    def test_extrapolate_beyond(self) -> None:
        # t > 1 should extrapolate
        result = bearing.interpolate(350, 10, 2.0)
        assert result == pytest.approx(30.0)


class TestWithin:
    """Tests for bearing.within()."""

    def test_within_tolerance_same(self) -> None:
        assert bearing.within(5, 5, 10) is True

    def test_within_clockwise(self) -> None:
        assert bearing.within(5, 0, 10) is True

    def test_within_counterclockwise(self) -> None:
        assert bearing.within(355, 0, 10) is True

    def test_outside_tolerance(self) -> None:
        assert bearing.within(20, 0, 10) is False

    def test_edge_of_tolerance(self) -> None:
        assert bearing.within(10, 0, 10) is True

    def test_just_outside_tolerance(self) -> None:
        assert bearing.within(10.1, 0, 10) is False

    def test_across_180(self) -> None:
        assert bearing.within(175, 180, 10) is True
        assert bearing.within(185, 180, 10) is True
        assert bearing.within(170, 180, 10) is True
        assert bearing.within(169, 180, 10) is False


class TestOpposite:
    """Tests for bearing.opposite()."""

    def test_north_to_south(self) -> None:
        assert bearing.opposite(0) == pytest.approx(180.0)

    def test_east_to_west(self) -> None:
        assert bearing.opposite(90) == pytest.approx(270.0)

    def test_south_to_north(self) -> None:
        assert bearing.opposite(180) == pytest.approx(0.0)

    def test_west_to_east(self) -> None:
        assert bearing.opposite(270) == pytest.approx(90.0)

    def test_northeast_to_southwest(self) -> None:
        assert bearing.opposite(45) == pytest.approx(225.0)

    def test_near_north_crosses_zero(self) -> None:
        assert bearing.opposite(350) == pytest.approx(170.0)

    def test_reciprocal_is_alias(self) -> None:
        # reciprocal should be exactly the same function as opposite
        assert bearing.reciprocal(45) == bearing.opposite(45)
        assert bearing.reciprocal is bearing.opposite

    def test_double_opposite_returns_original(self) -> None:
        original = 123.4
        result = bearing.opposite(bearing.opposite(original))
        assert result == pytest.approx(original)


class TestNormalizeMany:
    """Tests for bearing.normalize_many()."""

    def test_multiple_values(self) -> None:
        result = bearing.normalize_many([710, -10, 360])
        assert result == [pytest.approx(350.0), pytest.approx(350.0), pytest.approx(0.0)]

    def test_empty_list(self) -> None:
        assert bearing.normalize_many([]) == []

    def test_single_value(self) -> None:
        assert bearing.normalize_many([710]) == [pytest.approx(350.0)]


class TestDiffMany:
    """Tests for bearing.diff_many()."""

    def test_multiple_pairs(self) -> None:
        result = bearing.diff_many([(350, 10), (10, 350)])
        assert result == [pytest.approx(20.0), pytest.approx(-20.0)]

    def test_empty_list(self) -> None:
        assert bearing.diff_many([]) == []

    def test_single_pair(self) -> None:
        assert bearing.diff_many([(350, 10)]) == [pytest.approx(20.0)]
