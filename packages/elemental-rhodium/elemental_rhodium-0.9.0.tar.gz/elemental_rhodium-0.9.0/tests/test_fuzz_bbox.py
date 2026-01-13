
import random
from rhodium import bbox
from rhodium.bbox import BBox, Point

def random_lng() -> float:
    return random.uniform(-180, 180)

def random_lat() -> float:
    return random.uniform(-90, 90)

def random_point() -> Point:
    return Point(lng=random_lng(), lat=random_lat())

def random_bbox() -> BBox:
    w = random_lng()
    e = random_lng()
    s = random_lat()
    n = random_lat()
    if s > n:
        s, n = n, s
    return BBox(west=w, east=e, south=s, north=n)

def contains_approx(box: BBox, point: Point, tol: float = 1e-9) -> bool:
    """Check if point is in box with tolerance."""
    # Check lat
    if not (box.south - tol <= point.lat <= box.north + tol):
        return False
    
    # Check lng
    # If box covers world
    if bbox.width(box) >= 360 - tol:
        return True
        
    w = bbox.lng_mod.normalize(box.west)
    e = bbox.lng_mod.normalize(box.east)
    p = bbox.lng_mod.normalize(point.lng)
    
    if w > e: # crosses
        # p >= w OR p <= e
        # With tolerance: p >= w - tol OR p <= e + tol
        # But we need to handle wrap around 180 for strict inequality
        # easier to use distance?
        # If p is in [w, 180] or [-180, e]
        pass
    
    # Use built-in contains but extend box slightly? 
    # Or just rely on logic:
    # distance from box?
    
    # Simplest: use rhodium.lng.within logic manually
    # Normalize everything to [0, 360) relative to west?
    
    # Let's verify strict contains first, if fails, verify distance to edge is small.
    if bbox.contains(box, point):
        return True
        
    # Check distance to edges
    # If point is within tolerance of any edge, accept it.
    # This is complex. 
    # Let's just expand the box slightly for the check.
    # But strictly speaking, union should contain points.
    # Expanding the box is hard with wrapping.
    
    # Pragmactic approach: 
    # If contains fails, check if point is close to west, east, south, or north boundaries.
    
    # Lat check passed above (approx).
    
    # Lng check:
    diff_w = abs(bbox.lng_mod.diff(p, w))
    diff_e = abs(bbox.lng_mod.diff(p, e))
    if diff_w < tol or diff_e < tol:
        return True
        
    return False

class TestFuzzBBox:
    """Fuzz tests for bbox invariants."""

    def test_union_invariants(self) -> None:
        """
        Invariant: union(A, B) must contain both A and B.
        """
        random.seed(42)  # Deterministic seed
        for _ in range(1000):
            a = random_bbox()
            b = random_bbox()
            
            u = bbox.union(a, b)
            
            # Check containment by checking corners of A and B
            # Note: Checking box containment is stricter, but corners are good proxies
            corners_a = [
                Point(lng=a.west, lat=a.south),
                Point(lng=a.east, lat=a.north),
                Point(lng=a.west, lat=a.north),
                Point(lng=a.east, lat=a.south),
            ]
            for p in corners_a:
                assert contains_approx(u, p), f"Union {u} failed to contain corner {p} of box {a}"

            corners_b = [
                Point(lng=b.west, lat=b.south),
                Point(lng=b.east, lat=b.north),
                Point(lng=b.west, lat=b.north),
                Point(lng=b.east, lat=b.south),
            ]
            for p in corners_b:
                assert contains_approx(u, p), f"Union {u} failed to contain corner {p} of box {b}"

    def test_intersection_invariants(self) -> None:
        """
        Invariant: If intersection(A, B) exists, it must be contained in both A and B.
        """
        random.seed(42)
        for _ in range(1000):
            a = random_bbox()
            b = random_bbox()
            
            i = bbox.intersection(a, b)
            
            if i is None:
                continue
                
            # Intersection center must be in A and B
            c = bbox.center(i)
            assert contains_approx(a, c), f"Intersection center {c} not in A {a}. B was {b}. Intersection was {i}"
            assert contains_approx(b, c), f"Intersection center {c} not in B {b}. A was {a}. Intersection was {i}"
            
            # Intersection corners must be in A or B (depending on which edge defined them)
            # Actually, every point in I must be in A AND B.
            corners = [
                Point(lng=i.west, lat=i.south),
                Point(lng=i.east, lat=i.north),
            ]
            for p in corners:
                assert contains_approx(a, p), f"Intersection corner {p} not in {a}"
                assert contains_approx(b, p), f"Intersection corner {p} not in {b}"

    def test_width_additivity(self) -> None:
        """
        Invariant: width(union(A, B)) <= width(A) + width(B) + gap? 
        No, that's not strictly true due to wrapping.
        Invariant: width(union(A, B)) >= max(width(A), width(B))
        """
        random.seed(42)
        for _ in range(1000):
            a = random_bbox()
            b = random_bbox()
            
            u = bbox.union(a, b)
            
            wa = bbox.width(a)
            wb = bbox.width(b)
            wu = bbox.width(u)
            
            # Floating point leniency
            assert wu >= wa - 1e-9, f"Union width {wu} smaller than box A width {wa}"
            assert wu >= wb - 1e-9, f"Union width {wu} smaller than box B width {wb}"

    def test_center_contained(self) -> None:
        """
        Invariant: center(A) must be contained in A.
        (This ensures we didn't calculate the 'long way' center)
        """
        random.seed(42)
        for _ in range(1000):
            a = random_bbox()
            c = bbox.center(a)
            
            assert bbox.contains(a, c), f"Center {c} not inside box {a}"
