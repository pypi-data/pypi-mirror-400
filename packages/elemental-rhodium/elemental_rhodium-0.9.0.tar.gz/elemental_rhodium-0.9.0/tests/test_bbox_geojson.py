from rhodium import bbox
from rhodium.bbox import BBox, Point, from_geojson
import pytest

def test_from_geojson_bbox_array():
    data = [170, 0, -170, 10]
    box = from_geojson(data)
    assert box == BBox(west=170.0, east=-170.0, south=0.0, north=10.0)

def test_from_geojson_feature_bbox():
    data = {
        "type": "Feature",
        "bbox": [170, 0, -170, 10],
        "geometry": None
    }
    box = from_geojson(data)
    assert box == BBox(west=170.0, east=-170.0, south=0.0, north=10.0)

def test_from_geojson_polygon():
    # A simple polygon around 0,0
    data = {
        "type": "Polygon",
        "coordinates": [[
            [0, 0],
            [10, 0],
            [10, 10],
            [0, 10],
            [0, 0]
        ]]
    }
    box = from_geojson(data)
    assert box == BBox(west=0.0, east=10.0, south=0.0, north=10.0)

def test_from_geojson_polygon_crossing_antimeridian():
    # Polygon crossing 180
    data = {
        "type": "Polygon",
        "coordinates": [[
            [170, 0],
            [-170, 0],
            [-170, 10],
            [170, 10],
            [170, 0]
        ]]
    }
    box = from_geojson(data)
    assert box.west == 170.0
    assert box.east == -170.0
    assert box.south == 0.0
    assert box.north == 10.0

def test_from_geojson_feature_geometry():
    data = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [15, 45]
        }
    }
    box = from_geojson(data)
    assert box == BBox(west=15.0, east=15.0, south=45.0, north=45.0)

def test_from_geojson_invalid():
    with pytest.raises(ValueError):
        from_geojson("invalid")
    
    with pytest.raises(ValueError):
        from_geojson([1, 2, 3])  # too short

def test_roundtrip():
    box = BBox(west=170, east=-170, south=0, north=10)
    geo = box.to_geojson()
    # to_geojson returns a geometry dict
    box2 = from_geojson(geo)
    assert box == box2
