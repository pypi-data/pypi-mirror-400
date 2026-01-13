"""Tests for rhodium.lng module."""

import pytest

from rhodium import lng


class TestNormalize:
    """Tests for lng.normalize()."""

    def test_positive_overflow(self) -> None:
        assert lng.normalize(190) == pytest.approx(-170.0)

    def test_negative_overflow(self) -> None:
        assert lng.normalize(-190) == pytest.approx(170.0)

    def test_positive_180(self) -> None:
        # +180 stays as +180
        assert lng.normalize(180) == pytest.approx(180.0)

    def test_negative_180(self) -> None:
        # -180 becomes +180
        assert lng.normalize(-180) == pytest.approx(180.0)

    def test_zero(self) -> None:
        assert lng.normalize(0) == pytest.approx(0.0)

    def test_normal_positive(self) -> None:
        assert lng.normalize(90) == pytest.approx(90.0)

    def test_normal_negative(self) -> None:
        assert lng.normalize(-90) == pytest.approx(-90.0)

    def test_large_positive(self) -> None:
        assert lng.normalize(540) == pytest.approx(180.0)

    def test_large_negative(self) -> None:
        assert lng.normalize(-540) == pytest.approx(180.0)

    def test_360_wrap(self) -> None:
        assert lng.normalize(360) == pytest.approx(0.0)


class TestDiff:
    """Tests for lng.diff()."""

    def test_eastward_across_antimeridian(self) -> None:
        # 170° to -170° going east is +20°
        assert lng.diff(170, -170) == pytest.approx(20.0)

    def test_westward_across_antimeridian(self) -> None:
        # -170° to 170° going west is -20°
        assert lng.diff(-170, 170) == pytest.approx(-20.0)

    def test_same_longitude(self) -> None:
        assert lng.diff(45, 45) == pytest.approx(0.0)

    def test_small_eastward(self) -> None:
        assert lng.diff(-10, 10) == pytest.approx(20.0)

    def test_small_westward(self) -> None:
        assert lng.diff(10, -10) == pytest.approx(-20.0)

    def test_opposite_longitudes(self) -> None:
        # 0° to 180° is exactly 180°
        assert lng.diff(0, 180) == pytest.approx(180.0)

    def test_near_antimeridian_east(self) -> None:
        assert lng.diff(179, -179) == pytest.approx(2.0)

    def test_near_antimeridian_west(self) -> None:
        assert lng.diff(-179, 179) == pytest.approx(-2.0)


class TestMean:
    """Tests for lng.mean()."""

    def test_near_antimeridian(self) -> None:
        # Mean of 170° and -170° should be 180°
        result = lng.mean([170, -170])
        assert result == pytest.approx(180.0, abs=1e-9)

    def test_opposite_longitudes(self) -> None:
        # Mean of 0° and 180° is undefined
        assert lng.mean([0, 180]) is None

    def test_empty_list(self) -> None:
        assert lng.mean([]) is None

    def test_single_value(self) -> None:
        result = lng.mean([45])
        assert result == pytest.approx(45.0)

    def test_same_values(self) -> None:
        result = lng.mean([90, 90, 90])
        assert result == pytest.approx(90.0)

    def test_around_zero(self) -> None:
        result = lng.mean([-10, 10])
        assert result == pytest.approx(0.0, abs=1e-9)

    def test_negative_mean(self) -> None:
        result = lng.mean([-80, -100])
        assert result == pytest.approx(-90.0)


class TestWeightedMean:
    """Tests for lng.weighted_mean()."""

    def test_strong_pull(self) -> None:
        # [170, -170] (span 20 degrees across 180). Midpoint 180.
        # With weights [3, 1], mean should be closer to 170.
        # 170 + (20/4)*1 = 175? Let's rely on vectors.
        # Vector 1: 3 * (cos(170), sin(170))
        # Vector 2: 1 * (cos(-170), sin(-170))
        # This will be symmetric around X axis, so Y component cancels if weights equal.
        # With unequal weights, it pulls towards stronger side.
        result = lng.weighted_mean([170, -170], [3, 1])
        assert result == pytest.approx(175.0, abs=0.1)

    def test_equal_weights(self) -> None:
        # Should match regular mean
        result = lng.weighted_mean([170, -170], [1, 1])
        assert result == pytest.approx(180.0)

    def test_zero_weight_ignored(self) -> None:
        result = lng.weighted_mean([0, 90], [1, 0])
        assert result == pytest.approx(0.0)

    def test_opposite_cancel(self) -> None:
        # Equal weights on opposite directions -> None
        assert lng.weighted_mean([0, 180], [1, 1]) is None

    def test_length_mismatch(self) -> None:
        with pytest.raises(ValueError, match="same length"):
            lng.weighted_mean([0, 90], [1])


class TestInterpolate:
    """Tests for lng.interpolate()."""

    def test_across_antimeridian_midpoint(self) -> None:
        # Midpoint between 170° and -170° is 180°
        assert lng.interpolate(170, -170, 0.5) == pytest.approx(180.0)

    def test_around_zero(self) -> None:
        assert lng.interpolate(-10, 10, 0.5) == pytest.approx(0.0)

    def test_start_point(self) -> None:
        assert lng.interpolate(100, -100, 0.0) == pytest.approx(100.0)

    def test_end_point(self) -> None:
        assert lng.interpolate(100, -100, 1.0) == pytest.approx(-100.0)

    def test_quarter_across_antimeridian(self) -> None:
        # 160° to -160° is 40° span, quarter is 170°
        result = lng.interpolate(160, -160, 0.25)
        assert result == pytest.approx(170.0)

    def test_not_crossing_antimeridian(self) -> None:
        # 0° to 100°, midpoint is 50°
        assert lng.interpolate(0, 100, 0.5) == pytest.approx(50.0)


class TestWithin:
    """Tests for lng.within()."""

    def test_within_near_antimeridian_negative(self) -> None:
        assert lng.within(-175, 180, 10) is True

    def test_within_near_antimeridian_positive(self) -> None:
        assert lng.within(175, 180, 10) is True

    def test_outside_tolerance(self) -> None:
        assert lng.within(0, 180, 10) is False

    def test_exactly_at_target(self) -> None:
        assert lng.within(180, 180, 10) is True

    def test_at_tolerance_boundary(self) -> None:
        assert lng.within(170, 180, 10) is True
        assert lng.within(169, 180, 10) is False

    def test_near_zero(self) -> None:
        assert lng.within(-5, 0, 10) is True
        assert lng.within(5, 0, 10) is True
        assert lng.within(15, 0, 10) is False


class TestNormalizeMany:
    """Tests for lng.normalize_many()."""

    def test_multiple_values(self) -> None:
        result = lng.normalize_many([190, -190, 180])
        assert result == [pytest.approx(-170.0), pytest.approx(170.0), pytest.approx(180.0)]

    def test_empty_list(self) -> None:
        assert lng.normalize_many([]) == []

    def test_single_value(self) -> None:
        assert lng.normalize_many([190]) == [pytest.approx(-170.0)]


class TestDiffMany:
    """Tests for lng.diff_many()."""

    def test_multiple_pairs(self) -> None:
        result = lng.diff_many([(170, -170), (-170, 170)])
        assert result == [pytest.approx(20.0), pytest.approx(-20.0)]

    def test_empty_list(self) -> None:
        assert lng.diff_many([]) == []

    def test_single_pair(self) -> None:
        assert lng.diff_many([(170, -170)]) == [pytest.approx(20.0)]
