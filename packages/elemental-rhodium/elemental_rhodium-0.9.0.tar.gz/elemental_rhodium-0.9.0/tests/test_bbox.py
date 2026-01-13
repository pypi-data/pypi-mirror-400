"""Tests for rhodium.bbox module."""

import pytest

from rhodium import bbox
from rhodium.bbox import BBox, Point


class TestCreate:
    """Tests for bbox.create()."""

    def test_simple_box(self) -> None:
        result = bbox.create(
            Point(lng=-10, lat=40),
            Point(lng=10, lat=50),
        )
        assert result == BBox(west=-10, east=10, south=40, north=50)

    def test_antimeridian_box(self) -> None:
        result = bbox.create(
            Point(lng=170, lat=-10),
            Point(lng=-170, lat=10),
        )
        assert result == BBox(west=170, east=-170, south=-10, north=10)


class TestFromPoints:
    """Tests for bbox.from_points()."""

    def test_empty_points_raises(self) -> None:
        with pytest.raises(ValueError):
            bbox.from_points([])

    def test_single_point(self) -> None:
        result = bbox.from_points([Point(lng=10, lat=20)])
        assert result == BBox(west=10, east=10, south=20, north=20)

    def test_two_points_normal(self) -> None:
        result = bbox.from_points([
            Point(lng=-10, lat=40),
            Point(lng=10, lat=50),
        ])
        assert result.south == 40
        assert result.north == 50
        # Width should be 20
        assert bbox.width(result) == pytest.approx(20.0)

    def test_points_crossing_antimeridian(self) -> None:
        # Points at 170° and -170° - should create a 20° wide box crossing antimeridian
        result = bbox.from_points([
            Point(lng=170, lat=0),
            Point(lng=-170, lat=10),
        ])
        assert bbox.width(result) == pytest.approx(20.0)
        assert bbox.crosses_antimeridian(result) is True

    def test_points_not_crossing_antimeridian(self) -> None:
        # Points at -170° and -150° should NOT cross
        result = bbox.from_points([
            Point(lng=-170, lat=0),
            Point(lng=-150, lat=10),
        ])
        assert bbox.width(result) == pytest.approx(20.0)
        assert bbox.crosses_antimeridian(result) is False

    def test_many_points(self) -> None:
        result = bbox.from_points([
            Point(lng=0, lat=0),
            Point(lng=10, lat=10),
            Point(lng=5, lat=5),
            Point(lng=-5, lat=-5),
        ])
        assert result.south == -5
        assert result.north == 10
        assert bbox.width(result) == pytest.approx(15.0)


class TestWidth:
    """Tests for bbox.width()."""

    def test_normal_box(self) -> None:
        box = BBox(west=-10, east=10, south=0, north=10)
        assert bbox.width(box) == pytest.approx(20.0)

    def test_antimeridian_crossing(self) -> None:
        box = BBox(west=170, east=-170, south=0, north=10)
        assert bbox.width(box) == pytest.approx(20.0)

    def test_zero_width(self) -> None:
        box = BBox(west=50, east=50, south=0, north=10)
        assert bbox.width(box) == pytest.approx(0.0)

    def test_global_box(self) -> None:
        box = BBox(west=-180, east=180, south=-90, north=90)
        assert bbox.width(box) == pytest.approx(360.0)


class TestHeight:
    """Tests for bbox.height()."""

    def test_normal_box(self) -> None:
        box = BBox(west=0, east=10, south=40, north=50)
        assert bbox.height(box) == pytest.approx(10.0)

    def test_zero_height(self) -> None:
        box = BBox(west=0, east=10, south=45, north=45)
        assert bbox.height(box) == pytest.approx(0.0)


class TestCrossesAntimeridian:
    """Tests for bbox.crosses_antimeridian()."""

    def test_crossing(self) -> None:
        box = BBox(west=170, east=-170, south=0, north=10)
        assert bbox.crosses_antimeridian(box) is True

    def test_not_crossing(self) -> None:
        box = BBox(west=-10, east=10, south=0, north=10)
        assert bbox.crosses_antimeridian(box) is False

    def test_at_antimeridian(self) -> None:
        box = BBox(west=180, east=-180, south=0, north=10)
        assert bbox.crosses_antimeridian(box) is True


class TestContains:
    """Tests for bbox.contains()."""

    def test_inside_normal_box(self) -> None:
        box = BBox(west=-10, east=10, south=0, north=20)
        assert bbox.contains(box, Point(lng=0, lat=10)) is True

    def test_outside_normal_box(self) -> None:
        box = BBox(west=-10, east=10, south=0, north=20)
        assert bbox.contains(box, Point(lng=20, lat=10)) is False

    def test_inside_antimeridian_box(self) -> None:
        box = BBox(west=170, east=-170, south=0, north=10)
        assert bbox.contains(box, Point(lng=180, lat=5)) is True
        assert bbox.contains(box, Point(lng=-180, lat=5)) is True
        assert bbox.contains(box, Point(lng=175, lat=5)) is True
        assert bbox.contains(box, Point(lng=-175, lat=5)) is True

    def test_outside_antimeridian_box(self) -> None:
        box = BBox(west=170, east=-170, south=0, north=10)
        assert bbox.contains(box, Point(lng=0, lat=5)) is False
        assert bbox.contains(box, Point(lng=100, lat=5)) is False

    def test_on_edge(self) -> None:
        box = BBox(west=-10, east=10, south=0, north=20)
        assert bbox.contains(box, Point(lng=-10, lat=10)) is True
        assert bbox.contains(box, Point(lng=10, lat=10)) is True
        assert bbox.contains(box, Point(lng=0, lat=0)) is True
        assert bbox.contains(box, Point(lng=0, lat=20)) is True

    def test_latitude_out_of_range(self) -> None:
        box = BBox(west=-10, east=10, south=0, north=20)
        assert bbox.contains(box, Point(lng=0, lat=-5)) is False
        assert bbox.contains(box, Point(lng=0, lat=25)) is False


class TestCenter:
    """Tests for bbox.center()."""

    def test_normal_box(self) -> None:
        box = BBox(west=-10, east=10, south=0, north=20)
        result = bbox.center(box)
        assert result.lng == pytest.approx(0.0)
        assert result.lat == pytest.approx(10.0)

    def test_antimeridian_box(self) -> None:
        box = BBox(west=170, east=-170, south=0, north=10)
        result = bbox.center(box)
        assert result.lng == pytest.approx(180.0)
        assert result.lat == pytest.approx(5.0)


class TestIntersects:
    """Tests for bbox.intersects()."""

    def test_overlapping_boxes(self) -> None:
        a = BBox(west=0, east=20, south=0, north=20)
        b = BBox(west=10, east=30, south=10, north=30)
        assert bbox.intersects(a, b) is True

    def test_non_overlapping_boxes(self) -> None:
        a = BBox(west=0, east=10, south=0, north=10)
        b = BBox(west=20, east=30, south=20, north=30)
        assert bbox.intersects(a, b) is False

    def test_touching_boxes(self) -> None:
        a = BBox(west=0, east=10, south=0, north=10)
        b = BBox(west=10, east=20, south=0, north=10)
        assert bbox.intersects(a, b) is True

    def test_one_inside_other(self) -> None:
        a = BBox(west=0, east=100, south=-50, north=50)
        b = BBox(west=10, east=20, south=10, north=20)
        assert bbox.intersects(a, b) is True

    def test_antimeridian_boxes_overlap(self) -> None:
        a = BBox(west=160, east=-160, south=0, north=10)
        b = BBox(west=170, east=-170, south=0, north=10)
        assert bbox.intersects(a, b) is True

    def test_both_crossing_antimeridian(self) -> None:
        a = BBox(west=170, east=-170, south=0, north=10)
        b = BBox(west=175, east=-175, south=0, north=10)
        assert bbox.intersects(a, b) is True


class TestIntersection:
    """Tests for bbox.intersection()."""

    def test_no_intersection(self) -> None:
        a = BBox(west=0, east=10, south=0, north=10)
        b = BBox(west=20, east=30, south=20, north=30)
        assert bbox.intersection(a, b) is None

    def test_simple_intersection(self) -> None:
        a = BBox(west=0, east=20, south=0, north=20)
        b = BBox(west=10, east=30, south=10, north=30)
        result = bbox.intersection(a, b)
        assert result is not None
        assert result.west == 10
        assert result.east == 20
        assert result.south == 10
        assert result.north == 20


class TestUnion:
    """Tests for bbox.union()."""

    def test_simple_union(self) -> None:
        a = BBox(west=0, east=10, south=0, north=10)
        b = BBox(west=20, east=30, south=20, north=30)
        result = bbox.union(a, b)
        assert result.south == 0
        assert result.north == 30
        # Longitude union should span from 0 to 30
        assert bbox.width(result) >= 30

    def test_overlapping_union(self) -> None:
        a = BBox(west=0, east=20, south=0, north=20)
        b = BBox(west=10, east=30, south=10, north=30)
        result = bbox.union(a, b)
        assert result.south == 0
        assert result.north == 30

    def test_one_inside_other(self) -> None:
        a = BBox(west=0, east=100, south=-50, north=50)
        b = BBox(west=10, east=20, south=10, north=20)
        result = bbox.union(a, b)
        assert result.west == 0
        assert result.east == 100
        assert result.south == -50
        assert result.north == 50


class TestIsValid:
    """Tests for bbox.is_valid()."""

    def test_valid_box(self) -> None:
        box = BBox(west=0, east=10, south=0, north=10)
        assert bbox.is_valid(box) is True

    def test_valid_antimeridian_box(self) -> None:
        box = BBox(west=170, east=-170, south=0, north=10)
        assert bbox.is_valid(box) is True

    def test_invalid_south_greater_than_north(self) -> None:
        from rhodium import InvalidBBoxError
        with pytest.raises(InvalidBBoxError, match="south.*cannot be greater than north"):
            BBox(west=0, east=10, south=50, north=10)

    def test_invalid_latitude_out_of_range(self) -> None:
        from rhodium import InvalidLatitudeError
        with pytest.raises(InvalidLatitudeError):
            BBox(west=0, east=10, south=-100, north=10)

    def test_invalid_nan(self) -> None:
        import math
        from rhodium import InvalidLongitudeError
        with pytest.raises(InvalidLongitudeError):
            BBox(west=math.nan, east=10, south=0, north=10)


class TestValidation:
    """Tests for input validation."""

    def test_create_with_invalid_latitude(self) -> None:
        with pytest.raises(ValueError, match="must be between -90 and 90"):
            bbox.create(
                Point(lng=0, lat=100),  # Invalid latitude
                Point(lng=10, lat=50),
            )

    def test_create_with_nan(self) -> None:
        import math
        with pytest.raises(ValueError, match="NaN"):
            bbox.create(
                Point(lng=math.nan, lat=40),
                Point(lng=10, lat=50),
            )

    def test_create_with_south_greater_than_north(self) -> None:
        with pytest.raises(ValueError, match="cannot be greater"):
            bbox.create(
                Point(lng=0, lat=50),  # south
                Point(lng=10, lat=40),  # north < south
            )

    def test_from_points_with_invalid_latitude(self) -> None:
        with pytest.raises(ValueError, match="must be between -90 and 90"):
            bbox.from_points([
                Point(lng=0, lat=100),  # Invalid
            ])

    def test_contains_normalizes_point(self) -> None:
        # contains() normalizes the point's longitude
        box = BBox(west=170, east=-170, south=0, north=10)
        # Point at 540 (normalizes to 180) should be inside
        assert bbox.contains(box, Point(lng=540, lat=5)) is True
        # Point at 360 (normalizes to 0) should be outside
        assert bbox.contains(box, Point(lng=360, lat=5)) is False


class TestBBoxMethods:
    """Tests for BBox instance methods."""

    def test_pad_simple(self) -> None:
        box = BBox(west=0, east=10, south=0, north=10)
        padded = box.pad(5)
        assert padded.west == pytest.approx(-5.0)
        assert padded.east == pytest.approx(15.0)
        assert padded.south == pytest.approx(-5.0)
        assert padded.north == pytest.approx(15.0)

    def test_pad_clamping(self) -> None:
        box = BBox(west=0, east=10, south=85, north=85)
        padded = box.pad(10)
        assert padded.north == pytest.approx(90.0)  # Clamped
        assert padded.south == pytest.approx(75.0)

    def test_pad_crossing_antimeridian(self) -> None:
        box = BBox(west=175, east=-175, south=0, north=10) # Width 10
        padded = box.pad(5)
        # West: 175 - 5 = 170
        # East: -175 + 5 = -170
        # Width: (180-170) + (180-170) = 10 + 10 = 20. (Original 10 + 2*5 = 20).
        assert padded.west == pytest.approx(170.0)
        assert padded.east == pytest.approx(-170.0)

    def test_pad_full_world(self) -> None:
        box = BBox(west=0, east=10, south=0, north=10)
        padded = box.pad(200) # Expands by 400 degrees -> full world
        assert padded.west == -180.0
        assert padded.east == 180.0
        assert padded.south == -90.0
        assert padded.north == 90.0 # Clamped

    def test_to_geojson(self) -> None:
        box = BBox(west=0, east=10, south=0, north=10)
        gj = box.to_geojson()
        assert gj["type"] == "Polygon"
        assert len(gj["coordinates"]) == 1
        ring = gj["coordinates"][0]
        assert len(ring) == 5
        assert ring[0] == [0, 0] # SW
        assert ring[1] == [10, 0] # SE
        assert ring[2] == [10, 10] # NE
        assert ring[3] == [0, 10] # NW
        assert ring[4] == [0, 0] # SW (closed)


class TestExpand:
    """Tests for bbox.expand()."""

    def test_point_already_inside(self) -> None:
        box = BBox(west=0, east=10, south=0, north=10)
        point = Point(lng=5, lat=5)
        result = bbox.expand(box, point)
        # Should return the same box since point is inside
        assert result == box

    def test_expand_east(self) -> None:
        box = BBox(west=0, east=10, south=0, north=10)
        point = Point(lng=15, lat=5)
        result = bbox.expand(box, point)
        assert result.west == pytest.approx(0.0)
        assert result.east == pytest.approx(15.0)
        assert result.south == pytest.approx(0.0)
        assert result.north == pytest.approx(10.0)

    def test_expand_west(self) -> None:
        box = BBox(west=0, east=10, south=0, north=10)
        point = Point(lng=-5, lat=5)
        result = bbox.expand(box, point)
        assert result.west == pytest.approx(-5.0)
        assert result.east == pytest.approx(10.0)

    def test_expand_north(self) -> None:
        box = BBox(west=0, east=10, south=0, north=10)
        point = Point(lng=5, lat=15)
        result = bbox.expand(box, point)
        assert result.north == pytest.approx(15.0)
        assert result.south == pytest.approx(0.0)

    def test_expand_south(self) -> None:
        box = BBox(west=0, east=10, south=0, north=10)
        point = Point(lng=5, lat=-5)
        result = bbox.expand(box, point)
        assert result.south == pytest.approx(-5.0)
        assert result.north == pytest.approx(10.0)

    def test_expand_corner(self) -> None:
        box = BBox(west=0, east=10, south=0, north=10)
        point = Point(lng=20, lat=20)
        result = bbox.expand(box, point)
        assert result.west == pytest.approx(0.0)
        assert result.east == pytest.approx(20.0)
        assert result.south == pytest.approx(0.0)
        assert result.north == pytest.approx(20.0)

    def test_expand_with_antimeridian_crossing_box(self) -> None:
        box = BBox(west=170, east=-170, south=0, north=10)
        point = Point(lng=175, lat=5)
        # Point is inside (175 is between 170 and -170 going east)
        result = bbox.expand(box, point)
        assert result == box

    def test_expand_antimeridian_box_to_include_outside_point(self) -> None:
        box = BBox(west=170, east=-170, south=0, north=10)
        # 0 is outside (between -170 and 170)
        point = Point(lng=0, lat=5)
        result = bbox.expand(box, point)
        # Should expand to include 0
        assert bbox.contains(result, point)
