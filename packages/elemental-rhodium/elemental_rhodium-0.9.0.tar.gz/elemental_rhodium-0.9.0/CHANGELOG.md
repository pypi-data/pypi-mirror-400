# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0] - 2026-01-04

### Beta release - API stabilization

This beta release represents feature-complete functionality with stabilized APIs. Seeking community feedback before committing to v1.0.0 API guarantees.

**Features:**

- **Bearing arithmetic**: `normalize()`, `diff()`, `mean()`, `interpolate()`, `opposite()`, `within()`, `normalize_many()`, `diff_many()`
- **Longitude arithmetic**: `normalize()`, `diff()`, `mean()`, `interpolate()` with antimeridian handling
- **Latitude operations**: `clamp()`, `is_valid()`, `validate()`, `midpoint()`, `within()`, `hemisphere()`, `clamp_many()`
- **Bounding boxes**: `create()`, `from_points()`, `width()`, `height()`, `contains()`, `intersects()`, `intersection()`, `union()`, `expand()`, `crosses_antimeridian()`, `center()`
- **Python GIS ecosystem integration**: `Point` and `BBox` support `__geo_interface__` protocol for compatibility with shapely, fiona, and other geospatial libraries
- **Pythonic property access**: `BBox` provides convenient properties (`.width`, `.height`, `.center_point`, `.crosses_antimeridian`) alongside functional API
- **Exception hierarchy**: `RhodiumError`, `InvalidCoordinateError`, `InvalidLatitudeError`, `InvalidLongitudeError`, `InvalidBearingError`, `InvalidBBoxError`, `EmptyInputError`
- **Type safety**: Full type hints with `py.typed` marker
- **Zero dependencies**: Pure Python standard library only

**Testing & Quality:**

- 206 unit tests covering all API functions
- Property-based tests with Hypothesis for mathematical correctness
- 95%+ code coverage requirement
- Tested on Python 3.9, 3.10, 3.11, 3.12, 3.13
- Type checking with mypy
- Linting with ruff
- Pre-commit hooks enabled
- Benchmarking suite

**Quality Improvements:**

- Dataclass validation: `Point` and `BBox` now validate coordinates on construction
- Better exception messages with context
- Performance documentation (~50-200ns per operation)
- Numerical precision guarantees documented
- Security policy (SECURITY.md) with responsible disclosure process

**Known Limitations (documented):**

- Not optimized for bulk processing (100k+ coordinates)
- Subject to standard floating-point precision limits
- No geodesic distance calculations (use pyproj for that)
- No point-in-polygon except bounding boxes (use shapely for that)

**API Status:**

APIs are **stable but not frozen**. Minor breaking changes may occur before v1.0.0 based on community feedback. Use in production at your own risk, or pin to exact version.
