"""Bounding box operations with antimeridian support."""

from __future__ import annotations

from typing import Any
from dataclasses import dataclass

from rhodium import lng as lng_mod
from rhodium._validation import validate_latitude, validate_longitude
from rhodium._exceptions import InvalidBBoxError, EmptyInputError

__all__ = [
    "Point",
    "BBox",
    "create",
    "from_points",
    "from_geojson",
    "width",
    "height",
    "crosses_antimeridian",
    "contains",
    "center",
    "intersects",
    "intersection",
    "union",
    "expand",
    "is_valid",
]


@dataclass(frozen=True)
class Point:
    """A geographic point with longitude and latitude.

    Validates coordinates on construction. Raises InvalidLongitudeError
    or InvalidLatitudeError if coordinates are invalid.
    """

    lng: float
    lat: float

    def __post_init__(self) -> None:
        """Validate coordinates."""
        validate_longitude(self.lng, "lng")
        validate_latitude(self.lat, "lat")

    @property
    def __geo_interface__(self) -> dict[str, Any]:
        """
        Return GeoJSON representation following the Python geo_interface protocol.

        This allows Point to be used with libraries like shapely, fiona, and others
        that support the __geo_interface__ standard.
        """
        return {
            "type": "Point",
            "coordinates": [self.lng, self.lat]
        }


@dataclass(frozen=True)
class BBox:
    """A bounding box defined by west, east, south, north edges.

    Validates coordinates on construction. Raises InvalidLongitudeError,
    InvalidLatitudeError, or InvalidBBoxError if invalid.
    """

    west: float
    east: float
    south: float
    north: float

    def __post_init__(self) -> None:
        """Validate bounding box."""
        validate_longitude(self.west, "west")
        validate_longitude(self.east, "east")
        validate_latitude(self.south, "south")
        validate_latitude(self.north, "north")
        if self.south > self.north:
            raise InvalidBBoxError(f"south ({self.south}) cannot be greater than north ({self.north})")

    def pad(self, degrees: float) -> BBox:
        """
        Return a new BBox padded by the given degrees on all sides.
        
        Clamps latitude to [-90, 90].
        If longitude width exceeds 360, returns a full-width box (-180, 180).
        """
        new_south = max(-90.0, self.south - degrees)
        new_north = min(90.0, self.north + degrees)
        
        # Check current width
        w = self.east - self.west
        if w < 0:
            w += 360
            
        if w + (2 * degrees) >= 360:
            return BBox(west=-180.0, east=180.0, south=new_south, north=new_north)
            
        new_west = lng_mod.normalize(self.west - degrees)
        new_east = lng_mod.normalize(self.east + degrees)
        
        return BBox(west=new_west, east=new_east, south=new_south, north=new_north)

    @property
    def width(self) -> float:
        """Return the width of the bounding box in degrees (antimeridian-aware)."""
        return width(self)

    @property
    def height(self) -> float:
        """Return the height of the bounding box in degrees."""
        return height(self)

    @property
    def center_point(self) -> Point:
        """Return the center point of the bounding box."""
        return center(self)

    @property
    def crosses_antimeridian(self) -> bool:
        """Return True if the bounding box crosses the antimeridian (±180°)."""
        return crosses_antimeridian(self)

    def to_geojson(self) -> dict[str, Any]:
        """
        Return a GeoJSON Polygon geometry representing this bounding box.

        Note: If the box crosses the antimeridian, this returns a single Polygon
        with coordinates that may look "inverted" to some parsers (west > east).
        RFC 7946 suggests splitting, but many clients support crossing boxes.
        """
        # Counter-clockwise ring: SW -> SE -> NE -> NW -> SW
        coords = [
            [self.west, self.south],
            [self.east, self.south],
            [self.east, self.north],
            [self.west, self.north],
            [self.west, self.south],
        ]
        return {
            "type": "Polygon",
            "coordinates": [coords]
        }

    @property
    def __geo_interface__(self) -> dict[str, Any]:
        """
        Return GeoJSON representation following the Python geo_interface protocol.

        This allows BBox to be used with libraries like shapely, fiona, and others
        that support the __geo_interface__ standard.
        """
        return self.to_geojson()


def validate_point(point: Point, name: str = "point") -> None:
    """Validate a point has finite coordinates and valid latitude."""
    validate_longitude(point.lng, f"{name}.lng")
    validate_latitude(point.lat, f"{name}.lat")


def validate_bbox(box: BBox, name: str = "bbox") -> None:
    """Validate a bounding box has finite coordinates and valid latitudes."""
    validate_longitude(box.west, f"{name}.west")
    validate_longitude(box.east, f"{name}.east")
    validate_latitude(box.south, f"{name}.south")
    validate_latitude(box.north, f"{name}.north")
    if box.south > box.north:
        raise InvalidBBoxError(
            f"{name}.south ({box.south}) cannot be greater than {name}.north ({box.north})"
        )


def is_valid(box: BBox) -> bool:
    """
    Check if a bounding box has valid coordinates.

    Returns True if:
    - All coordinates are finite (not NaN or infinite)
    - Latitudes are within [-90, 90]
    - south <= north

    Examples:
        >>> is_valid(BBox(west=0, east=10, south=0, north=10))
        True
        >>> is_valid(BBox(west=0, east=10, south=50, north=10))
        False
    """
    from rhodium._exceptions import RhodiumError

    try:
        validate_bbox(box)
        return True
    except (ValueError, RhodiumError):
        return False


def create(west_point: Point, east_point: Point, validate: bool = True) -> BBox:
    """
    Create a bounding box from two corner points.

    The first point's longitude becomes the western edge, and the second
    point's longitude becomes the eastern edge. This allows creating boxes
    that cross the antimeridian.

    Args:
        west_point: Point defining western edge longitude and southern latitude
        east_point: Point defining eastern edge longitude and northern latitude
        validate: If True (default), validates coordinates are finite and correct.

    Examples:
        >>> create(Point(lng=-10, lat=40), Point(lng=10, lat=50))
        BBox(west=-10, east=10, south=40, north=50)
        >>> create(Point(lng=170, lat=0), Point(lng=-170, lat=10))  # crosses antimeridian
        BBox(west=170, east=-170, south=0, north=10)
    """
    if validate:
        validate_point(west_point, "west_point")
        validate_point(east_point, "east_point")

    box = BBox(
        west=west_point.lng,
        east=east_point.lng,
        south=west_point.lat,
        north=east_point.lat,
    )
    if validate and box.south > box.north:
        raise InvalidBBoxError(
            f"west_point.lat ({box.south}) cannot be greater than east_point.lat ({box.north})"
        )
    return box


def from_points(points: list[Point], validate: bool = True) -> BBox:
    """
    Create the smallest bounding box containing all points.

    Handles antimeridian crossing correctly by finding the smallest
    longitudinal span.

    Args:
        points: List of points to encompass
        validate: If True (default), validates all points.

    Raises:
        ValueError: If points list is empty or contains invalid coordinates (if validate=True).
    """
    if not points:
        raise EmptyInputError("Cannot create bbox from empty points list")

    if validate:
        for i, p in enumerate(points):
            validate_point(p, f"points[{i}]")

    if len(points) == 1:
        p = points[0]
        return BBox(west=p.lng, east=p.lng, south=p.lat, north=p.lat)

    # Latitude is simple - just min/max
    lats = [p.lat for p in points]
    south, north = min(lats), max(lats)

    # Longitude requires finding the smallest span
    lngs = sorted(set(lng_mod.normalize(p.lng) for p in points))

    if len(lngs) == 1:
        return BBox(west=lngs[0], east=lngs[0], south=south, north=north)

    # Find the largest gap between consecutive longitudes
    # The bbox should NOT include this gap
    max_gap = 0.0
    max_gap_idx = 0

    for i in range(len(lngs)):
        next_i = (i + 1) % len(lngs)
        # Gap from lngs[i] to lngs[next_i] going eastward
        if next_i == 0:
            # Wrap around: gap from last to first
            gap = (lngs[0] + 360) - lngs[-1]
        else:
            gap = lngs[next_i] - lngs[i]

        if gap > max_gap:
            max_gap = gap
            max_gap_idx = i

    # West is after the gap, east is before the gap
    west_idx = (max_gap_idx + 1) % len(lngs)
    east_idx = max_gap_idx

    return BBox(west=lngs[west_idx], east=lngs[east_idx], south=south, north=north)


def width(box: BBox) -> float:
    """
    Compute the width of the bounding box in degrees.

    Correctly handles boxes that cross the antimeridian.

    Examples:
        >>> width(BBox(west=170, east=-170, south=0, north=10))
        20.0
        >>> width(BBox(west=-10, east=10, south=0, north=10))
        20.0
    """
    w = box.east - box.west
    if w < 0:
        w += 360
    return w


def height(box: BBox) -> float:
    """
    Compute the height of the bounding box in degrees.

    Examples:
        >>> height(BBox(west=0, east=10, south=40, north=50))
        10.0
    """
    return box.north - box.south


def crosses_antimeridian(box: BBox) -> bool:
    """
    Check if the bounding box crosses the antimeridian.

    Examples:
        >>> crosses_antimeridian(BBox(west=170, east=-170, south=0, north=10))
        True
        >>> crosses_antimeridian(BBox(west=-10, east=10, south=0, north=10))
        False
    """
    return box.west > box.east


def contains(box: BBox, point: Point) -> bool:
    """
    Check if a point is inside the bounding box.

    Works correctly for boxes crossing the antimeridian.
    Normalizes both box bounds and point longitude for correct comparison.

    Examples:
        >>> contains(BBox(west=170, east=-170, south=0, north=10), Point(lng=180, lat=5))
        True
        >>> contains(BBox(west=170, east=-170, south=0, north=10), Point(lng=0, lat=5))
        False
        >>> contains(BBox(west=190, east=-170, south=0, north=10), Point(lng=-175, lat=5))
        True
    """
    lat = point.lat
    lng = lng_mod.normalize(point.lng)

    # Normalize box bounds for comparison
    west = lng_mod.normalize(box.west)
    east = lng_mod.normalize(box.east)

    # Check latitude first
    if lat < box.south or lat > box.north:
        return False

    # Check for full world longitude coverage
    if width(box) >= 360:
        return True

    # Check longitude - use normalized bounds
    west = lng_mod.normalize(box.west)
    east = lng_mod.normalize(box.east)

    if west > east:  # crosses antimeridian
        # Point must be >= west OR <= east
        return lng >= west or lng <= east
    else:
        return west <= lng <= east


def center(box: BBox) -> Point:
    """
    Compute the center point of the bounding box.

    Examples:
        >>> center(BBox(west=170, east=-170, south=0, north=10))
        Point(lng=180.0, lat=5.0)
    """
    lat = (box.south + box.north) / 2
    
    # Calculate longitude center respecting the West->East direction
    w = box.west
    e = box.east
    
    if w > e:
        # Crosses antimeridian: e.g. 350 to 10. Width is 20.
        # Center is 350 + 10 = 360 -> 0.
        # w + (360 - w + e) / 2
        # = w + 180 - w/2 + e/2
        # = 180 + w/2 + e/2
        # Easier: calculate width, add half width to west, normalize
        width = (e + 360) - w
    else:
        width = e - w
        
    mid_lng = lng_mod.normalize(w + width / 2)
    return Point(lng=mid_lng, lat=lat)


def intersects(a: BBox, b: BBox) -> bool:
    """
    Check if two bounding boxes intersect.

    Examples:
        >>> intersects(
        ...     BBox(west=0, east=20, south=0, north=20),
        ...     BBox(west=10, east=30, south=10, north=30)
        ... )
        True
    """
    # Check latitude overlap
    if a.north < b.south or b.north < a.south:
        return False

    # Check longitude overlap
    return _lng_ranges_overlap(a.west, a.east, b.west, b.east)


def _lng_ranges_overlap(w1: float, e1: float, w2: float, e2: float) -> bool:
    """Check if two longitude ranges overlap."""
    cross1 = w1 > e1
    cross2 = w2 > e2

    if not cross1 and not cross2:
        # Neither crosses antimeridian
        return w1 <= e2 and w2 <= e1
    elif cross1 and cross2:
        # Both cross antimeridian - they always overlap
        return True
    elif cross1:
        # Only first crosses: [w1, 180] U [-180, e1]
        return w2 <= e1 or e2 >= w1
    else:
        # Only second crosses: [w2, 180] U [-180, e2]
        return w1 <= e2 or e1 >= w2


def intersection(a: BBox, b: BBox) -> BBox | None:
    """
    Compute the intersection of two bounding boxes.

    Returns None if the boxes do not intersect.
    """
    if not intersects(a, b):
        return None

    # Latitude intersection is simple
    south = max(a.south, b.south)
    north = min(a.north, b.north)

    # Longitude intersection is complex with antimeridian
    west, east = _lng_range_intersection(a.west, a.east, b.west, b.east)

    return BBox(west=west, east=east, south=south, north=north)


def _lng_range_intersection(
    w1: float, e1: float, w2: float, e2: float
) -> tuple[float, float]:
    """Compute intersection of two longitude ranges."""
    cross1 = w1 > e1
    cross2 = w2 > e2

    if not cross1 and not cross2:
        # Neither crosses antimeridian
        return (max(w1, w2), min(e1, e2))
    elif cross1 and cross2:
        # Both cross - intersection also crosses
        # Take the more restrictive bounds
        return (max(w1, w2), min(e1, e2))
    elif cross1:
        # Only a crosses: check which part of a overlaps with b
        if w2 <= e1 and e2 >= w1:
            # b spans the antimeridian gap - intersection is disjoint ([w2, e1] and [w1, e2])
            # Return the largest segment
            width1 = e1 - w2
            width2 = e2 - w1
            if width1 >= width2:
                return (max(-180, w2), min(e1, e2))
            else:
                return (max(w1, w2), min(180, e2))
        elif w2 <= e1:
            # Overlap with eastern part of a
            return (max(-180, w2), min(e1, e2))
        else:
            # Overlap with western part of a
            return (max(w1, w2), min(180, e2))
    else:
        # Only b crosses
        if w1 <= e2 and e1 >= w2:
            # a overlaps both parts of b - intersection is disjoint ([w1, e2] and [w2, e1])
            # Return the largest segment
            width1 = e2 - w1
            width2 = e1 - w2
            if width1 >= width2:
                return (max(w1, -180), min(e2, 180)) # normalization usually not needed but safe
            else:
                return (max(w2, -180), min(e1, 180))
        elif w1 <= e2:
            return (max(-180, w1), min(e1, e2))
        else:
            return (max(w1, w2), min(180, e1))


def union(a: BBox, b: BBox) -> BBox:
    """
    Compute the smallest bounding box containing both input boxes.

    Examples:
        >>> union(
        ...     BBox(west=0, east=10, south=0, north=10),
        ...     BBox(west=20, east=30, south=20, north=30)
        ... )
        BBox(west=0, east=30, south=0, north=30)
    """
    # Latitude union is simple
    south = min(a.south, b.south)
    north = max(a.north, b.north)

    # Use from_points logic but we need to ensure we include all ranges
    # Actually, we need a different approach for union
    west, east = _lng_range_union(a.west, a.east, b.west, b.east)

    return BBox(west=west, east=east, south=south, north=north)


def expand(box: BBox, point: Point) -> BBox:
    """
    Return a new bounding box expanded to include the given point.

    If the point is already inside the box, returns the same box.
    Otherwise, returns the smallest box containing both the original
    box and the point.

    Examples:
        >>> expand(BBox(west=0, east=10, south=0, north=10), Point(lng=15, lat=5))
        BBox(west=0, east=15, south=0, north=10)
        >>> expand(BBox(west=0, east=10, south=0, north=10), Point(lng=5, lat=5))
        BBox(west=0, east=10, south=0, north=10)
    """
    if contains(box, point):
        return box

    # Use from_points with all corners plus the new point
    corners = [
        Point(lng=box.west, lat=box.south),
        Point(lng=box.west, lat=box.north),
        Point(lng=box.east, lat=box.south),
        Point(lng=box.east, lat=box.north),
        point,
    ]
    return from_points(corners, validate=False)


def from_geojson(data: dict[str, Any] | list[float] | tuple[float, ...]) -> BBox:
    """
    Create a bounding box from GeoJSON data.

    Supports:
    - BBox array: [west, south, east, north]
    - Geometry object (Polygon, Point, etc.): calculates bounds of all coordinates
    - Feature object: uses 'bbox' property or calculates from geometry

    Args:
        data: GeoJSON dictionary or bounding box list/tuple

    Returns:
        BBox object

    Raises:
        ValueError: If data format is not recognized or invalid
    """
    # Case 1: List/Tuple [west, south, east, north]
    if isinstance(data, (list, tuple)):
        if len(data) != 4:
            raise ValueError(
                "GeoJSON bbox array must have exactly 4 elements: [west, south, east, north]"
            )
        west, south, east, north = map(float, data)
        return BBox(west=west, east=east, south=south, north=north)

    if not isinstance(data, dict):
        raise ValueError(f"Unexpected type for GeoJSON data: {type(data)}")

    # Case 2: Feature with bbox
    if data.get("type") == "Feature":
        if "bbox" in data:
            return from_geojson(data["bbox"])
        if "geometry" in data and data["geometry"]:
            return from_geojson(data["geometry"])
        raise ValueError("GeoJSON Feature has no 'bbox' or 'geometry'")

    # Case 3: Geometry (Polygon, MultiPolygon, etc.) - extract all points
    # Recursive coordinate extraction
    def extract_points(coords: Any) -> list[Point]:
        points = []
        if not coords:
            return points

        # Check depth to see if we hit a [lng, lat] pair
        # A coordinate is a list/tuple of numbers, usually length 2 or 3
        if isinstance(coords[0], (int, float)):
            if len(coords) < 2:
                return []
            return [Point(lng=float(coords[0]), lat=float(coords[1]))]

        for child in coords:
            points.extend(extract_points(child))
        return points

    if "coordinates" in data:
        points = extract_points(data["coordinates"])
        if not points:
            raise EmptyInputError("GeoJSON geometry has no coordinates")
        return from_points(points)

    raise ValueError("GeoJSON object must be a Feature, Geometry, or bbox array")


def _lng_range_union(
    w1: float, e1: float, w2: float, e2: float
) -> tuple[float, float]:
    """Compute union of two longitude ranges, finding smallest containing span."""
    cross1 = w1 > e1
    cross2 = w2 > e2

    # If both cross antimeridian
    if cross1 and cross2:
        # Union also crosses, take outermost bounds
        w = min(w1, w2)
        e = max(e1, e2)
        if w <= e:
            # Union wrapped all the way around (covers full world)
            return (-180, 180)
        return (w, e)

    # Normalize to [0, 360) for easier calculation
    def to_360(lng: float) -> float:
        return lng if lng >= 0 else lng + 360

    def from_360(lng: float) -> float:
        return lng if lng <= 180 else lng - 360

    def get_ranges(w: float, e: float) -> list[tuple[float, float]]:
        # Handle full world case
        width = e - w
        if width < 0:
            width += 360
        if width >= 360:
            return [(0, 360)]
            
        start = to_360(w)
        end = to_360(e)
        if start <= end:
            return [(start, end)]
        else:
            return [(start, 360), (0, end)]

    ranges1 = get_ranges(w1, e1)
    ranges2 = get_ranges(w2, e2)

    intervals = ranges1 + ranges2
    
    # Merge overlapping intervals
    intervals.sort()
    if not intervals:
        return (0, 0)

    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    if len(merged) == 1:
        # Check if it covers full circle
        if merged[0][1] - merged[0][0] >= 360:
            return (-180, 180)

    # Find the largest gap to exclude
    gaps = []

    # Linear gaps between consecutive intervals
    for i in range(len(merged) - 1):
        gap_start = merged[i][1]
        gap_end = merged[i+1][0]
        gap_size = gap_end - gap_start
        gaps.append((gap_size, gap_end, gap_start))

    # Wrap gap from last end to first start
    wrap_gap_start = merged[-1][1]
    wrap_gap_end = merged[0][0]
    wrap_gap_size = (360 - wrap_gap_start) + wrap_gap_end
    gaps.append((wrap_gap_size, wrap_gap_end, wrap_gap_start))

    # Find largest gap
    max_gap = max(gaps, key=lambda x: x[0])
    
    if max_gap[0] < 1e-10:
        return (-180, 180)

    return (from_360(max_gap[1]), from_360(max_gap[2]))
