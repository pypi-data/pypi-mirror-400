"""Comprehensive benchmarks for rhodium core operations."""

import timeit
import random
from rhodium import bearing, lng, lat, bbox
from rhodium.bbox import Point, BBox


def generate_random_points(n: int) -> list[Point]:
    """Generate n random geographic points."""
    return [
        Point(lng=random.uniform(-180, 180), lat=random.uniform(-90, 90))
        for _ in range(n)
    ]


def generate_random_bearings(n: int) -> list[float]:
    """Generate n random bearings."""
    return [random.uniform(0, 360) for _ in range(n)]


def generate_random_longitudes(n: int) -> list[float]:
    """Generate n random longitudes."""
    return [random.uniform(-180, 180) for _ in range(n)]


# Pre-generate test data
random.seed(42)
POINTS_100 = generate_random_points(100)
POINTS_1000 = generate_random_points(1000)
BEARINGS_100 = generate_random_bearings(100)
LONGITUDES_100 = generate_random_longitudes(100)


# BBox benchmarks
def bench_bbox_create():
    p1 = Point(lng=10.0, lat=20.0)
    p2 = Point(lng=15.0, lat=25.0)
    bbox.create(p1, p2)


def bench_bbox_create_no_validate():
    p1 = Point(lng=10.0, lat=20.0)
    p2 = Point(lng=15.0, lat=25.0)
    bbox.create(p1, p2, validate=False)


def bench_bbox_direct():
    BBox(west=10.0, east=15.0, south=20.0, north=25.0)


def bench_bbox_from_points_100():
    bbox.from_points(POINTS_100)


def bench_bbox_from_points_1000():
    bbox.from_points(POINTS_1000)


def bench_bbox_contains():
    box = BBox(west=-10, east=10, south=-10, north=10)
    point = Point(lng=5, lat=5)
    bbox.contains(box, point)


def bench_bbox_contains_antimeridian():
    box = BBox(west=170, east=-170, south=-10, north=10)
    point = Point(lng=175, lat=5)
    bbox.contains(box, point)


def bench_bbox_intersects():
    a = BBox(west=0, east=20, south=0, north=20)
    b = BBox(west=10, east=30, south=10, north=30)
    bbox.intersects(a, b)


def bench_bbox_union():
    a = BBox(west=0, east=20, south=0, north=20)
    b = BBox(west=10, east=30, south=10, north=30)
    bbox.union(a, b)


def bench_bbox_center():
    box = BBox(west=170, east=-170, south=-10, north=10)
    bbox.center(box)


# Bearing benchmarks
def bench_bearing_normalize():
    bearing.normalize(710)


def bench_bearing_diff():
    bearing.diff(350, 10)


def bench_bearing_mean_100():
    bearing.mean(BEARINGS_100)


def bench_bearing_interpolate():
    bearing.interpolate(350, 20, 0.5)


def bench_bearing_opposite():
    bearing.opposite(45)


def bench_bearing_normalize_many():
    bearing.normalize_many(BEARINGS_100)


# Longitude benchmarks
def bench_lng_normalize():
    lng.normalize(190)


def bench_lng_diff():
    lng.diff(170, -170)


def bench_lng_mean_100():
    lng.mean(LONGITUDES_100)


def bench_lng_interpolate():
    lng.interpolate(170, -170, 0.5)


def bench_lng_normalize_many():
    lng.normalize_many(LONGITUDES_100)


# Latitude benchmarks
def bench_lat_clamp():
    lat.clamp(95)


def bench_lat_is_valid():
    lat.is_valid(45)


def bench_lat_clamp_many():
    lat.clamp_many([95, -100, 45, 0, 90, -90])


def run_benchmark(name: str, func, iterations: int = 100_000) -> None:
    """Run a single benchmark and print results."""
    time = timeit.timeit(func, number=iterations)
    ops_per_sec = iterations / time
    us_per_op = (time / iterations) * 1_000_000
    print(f"  {name:40} {us_per_op:8.3f} µs/op  ({ops_per_sec:>12,.0f} ops/s)")


if __name__ == "__main__":
    print("=" * 75)
    print("RHODIUM BENCHMARKS")
    print("=" * 75)

    print("\n--- BBox Operations ---")
    run_benchmark("bbox.create (validated)", bench_bbox_create)
    run_benchmark("bbox.create (no validate)", bench_bbox_create_no_validate)
    run_benchmark("BBox() direct construction", bench_bbox_direct)
    run_benchmark("bbox.from_points (100 points)", bench_bbox_from_points_100, 10_000)
    run_benchmark("bbox.from_points (1000 points)", bench_bbox_from_points_1000, 1_000)
    run_benchmark("bbox.contains", bench_bbox_contains)
    run_benchmark("bbox.contains (antimeridian)", bench_bbox_contains_antimeridian)
    run_benchmark("bbox.intersects", bench_bbox_intersects)
    run_benchmark("bbox.union", bench_bbox_union)
    run_benchmark("bbox.center", bench_bbox_center)

    print("\n--- Bearing Operations ---")
    run_benchmark("bearing.normalize", bench_bearing_normalize)
    run_benchmark("bearing.diff", bench_bearing_diff)
    run_benchmark("bearing.mean (100 angles)", bench_bearing_mean_100, 10_000)
    run_benchmark("bearing.interpolate", bench_bearing_interpolate)
    run_benchmark("bearing.opposite", bench_bearing_opposite)
    run_benchmark("bearing.normalize_many (100)", bench_bearing_normalize_many, 10_000)

    print("\n--- Longitude Operations ---")
    run_benchmark("lng.normalize", bench_lng_normalize)
    run_benchmark("lng.diff", bench_lng_diff)
    run_benchmark("lng.mean (100 longitudes)", bench_lng_mean_100, 10_000)
    run_benchmark("lng.interpolate", bench_lng_interpolate)
    run_benchmark("lng.normalize_many (100)", bench_lng_normalize_many, 10_000)

    print("\n--- Latitude Operations ---")
    run_benchmark("lat.clamp", bench_lat_clamp)
    run_benchmark("lat.is_valid", bench_lat_is_valid)
    run_benchmark("lat.clamp_many (6 values)", bench_lat_clamp_many)

    print("\n" + "=" * 75)
