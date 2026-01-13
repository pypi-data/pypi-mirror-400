"""Tests for __geo_interface__ protocol compliance."""

import pytest

from rhodium.bbox import Point, BBox


class TestPointGeoInterface:
    """Tests for Point.__geo_interface__."""

    def test_simple_point(self) -> None:
        p = Point(lng=-122.4, lat=37.8)
        geo = p.__geo_interface__
        assert geo["type"] == "Point"
        assert geo["coordinates"] == [-122.4, 37.8]

    def test_antimeridian_point(self) -> None:
        p = Point(lng=180, lat=0)
        geo = p.__geo_interface__
        assert geo["type"] == "Point"
        assert geo["coordinates"] == [180, 0]

    def test_negative_coords(self) -> None:
        p = Point(lng=-122.4, lat=-33.9)
        geo = p.__geo_interface__
        assert geo["type"] == "Point"
        assert geo["coordinates"] == [-122.4, -33.9]


class TestBBoxGeoInterface:
    """Tests for BBox.__geo_interface__."""

    def test_simple_bbox(self) -> None:
        box = BBox(west=0, east=10, south=0, north=10)
        geo = box.__geo_interface__
        assert geo["type"] == "Polygon"
        assert geo["coordinates"] == [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]]

    def test_antimeridian_bbox(self) -> None:
        box = BBox(west=170, east=-170, south=-10, north=10)
        geo = box.__geo_interface__
        assert geo["type"] == "Polygon"
        # Should preserve west > east for antimeridian crossing
        assert geo["coordinates"][0][0] == [170, -10]
        assert geo["coordinates"][0][1] == [-170, -10]

    def test_matches_to_geojson(self) -> None:
        box = BBox(west=0, east=10, south=0, north=10)
        assert box.__geo_interface__ == box.to_geojson()


class TestBBoxProperties:
    """Tests for BBox convenience properties."""

    def test_width_property(self) -> None:
        box = BBox(west=0, east=10, south=0, north=10)
        assert box.width == 10

    def test_height_property(self) -> None:
        box = BBox(west=0, east=10, south=0, north=10)
        assert box.height == 10

    def test_center_point_property(self) -> None:
        box = BBox(west=0, east=10, south=0, north=10)
        center = box.center_point
        assert center.lng == pytest.approx(5.0)
        assert center.lat == pytest.approx(5.0)

    def test_crosses_antimeridian_property_false(self) -> None:
        box = BBox(west=0, east=10, south=0, north=10)
        assert box.crosses_antimeridian is False

    def test_crosses_antimeridian_property_true(self) -> None:
        box = BBox(west=170, east=-170, south=0, north=10)
        assert box.crosses_antimeridian is True

    def test_antimeridian_width(self) -> None:
        box = BBox(west=170, east=-170, south=0, north=10)
        assert box.width == pytest.approx(20.0)

    def test_properties_match_functions(self) -> None:
        """Ensure properties return same values as module functions."""
        from rhodium import bbox

        box = BBox(west=-10, east=20, south=-5, north=15)

        assert box.width == bbox.width(box)
        assert box.height == bbox.height(box)
        assert box.center_point == bbox.center(box)
        assert box.crosses_antimeridian == bbox.crosses_antimeridian(box)
