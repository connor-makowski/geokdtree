# geokdtree — Developer Guide

## Project Purpose

`geokdtree` is a lightweight, high-performance spatial indexing library for Python designed to find the nearest geographic coordinate from datasets in log time:
- **Ultra-fast nearest-neighbor lookup** for `(latitude, longitude)` data without heavy GIS dependencies.
- **Cartesian KD-Tree** supporting N-dimensional points.
- **Optional C++ acceleration** via `nanobind` with transparent **pure Python fallback**.
- Zero external runtime dependencies.

---

> **IMPORTANT — DO NOT RUN A RELEASE CYCLE.** Do not bump versions, generate docs, build distributions, or publish to PyPI. Release steps are owner-only. If you think a release is needed, flag it and stop.

---

## Directory Layout (relevant files only)

```
geokdtree/
  __init__.py          # Package exports (GeoKDTree, KDTree) with C++ import & Python fallback
  geokdtree.py        # Pure Python GeoKDTree & spherical coordinate conversions
  kdtree.py           # Pure Python KDTree for N-dimensional Cartesian points
  core.py             # Pure Python recursive tree construction & nearest-neighbor search
  cpp/
    bindings/         # nanobind module entry point (geokdtree_bindings.cpp)
    src/              # C++ implementations (geokdtree.cpp, geokdtree.hpp)
test/
  test_install_type.py # Tests build type validation via env vars (GEOKDTREE_REQUIRE_CPP / PYTHON)
  test_geokdtree.py    # Unit tests for GeoKDTree (city lookups, poles, equator, consistency)
  test_kdtree.py       # Unit tests for Cartesian KDTree (1D, 2D, 3D, 4D, scale)
  test_core.py         # Unit tests for core recursive tree building and squared distance
utils/
  benchmark.py        # Performance benchmark suite comparing C++ vs Pure Python -> outputs benchmark.md
  prettify.py         # autoflake (unused imports) + black (line-length=80)
  docs.py             # Generate pdoc HTML docs — DO NOT RUN (release only)
benchmark.md          # Generated performance benchmarks across dataset scales
CMakeLists.txt        # CMake build configuration with nanobind & C++20
noxfile.py            # Nox sessions: runs pytest across Python 3.11–3.14 & PyPy3.11 (C++ & Pure Python)
pyproject.toml        # Project metadata, dependencies, black, pytest, and scikit-build configs
setup.cfg             # Version configuration mirrored from pyproject.toml
publish.sh            # PyPI publishing script — DO NOT RUN
```

---

## Development & Building

When modifying C++ code (`geokdtree/cpp/`) or building:
- **Do not investigate, build manually, or copy `.so` files.**
- Rebuild and reinstall cleanly in the dev environment:
  ```bash
  uv sync --extra dev --reinstall-package geokdtree
  ```
- To test or build in pure Python mode without compiling C++:
  ```bash
  GEOKDTREE_NO_BUILD=1 uv sync --extra dev --reinstall-package geokdtree
  ```

### Running Tests

- Run local test suite with `pytest`:
  ```bash
  uv run pytest
  ```
- Run full test matrix across Python versions (3.11–3.14, PyPy3.11) with `nox`:
  ```bash
  uv run nox
  ```
- Run a specific `nox` session:
  ```bash
  uv run nox -s tests-3.14
  ```

### Running Benchmarks

- Run the performance benchmarks to generate/update `benchmark.md`:
  ```bash
  uv run python utils/benchmark.py
  ```

### Formatting Code

- Format and clean up code:
  ```bash
  uv run python utils/prettify.py
  ```

---

## Core Architecture

### Key Files

**`geokdtree/__init__.py`** — package entry point:
- Attempts to import `GeoKDTree` and `KDTree` from the compiled `geokdtree.cpp` extension.
- Falls back transparently to `geokdtree.geokdtree.GeoKDTree` and `geokdtree.kdtree.KDTree` if C++ extension is unavailable.

**`geokdtree/geokdtree.py`** — pure Python geographic index:
- `GeoKDTree` — converts `(latitude, longitude)` points into 3D Cartesian coordinates `(x, y, z)` on a unit sphere, building a 3D KD-Tree with original coordinate indices preserved.
- `closest_idx(point)` — returns the index in the original points list of the nearest neighbor.
- `closest_point(point)` — returns the `(lat, lon)` tuple of the nearest neighbor.
- `closest_idx_per_quadrant(point)` — returns a dictionary of closest indices per quadrant (`ne`, `nw`, `se`, `sw`).
- `closest_point_per_quadrant(point)` — returns a dictionary of closest points per quadrant (`ne`, `nw`, `se`, `sw`).
- `__lat_lon_idx_to_xyz_idx__` — converts degrees `(lat, lon, idx)` to radians and unit sphere `(x, y, z, idx)`.

**`geokdtree/kdtree.py`** — pure Python Cartesian index:
- `KDTree` — N-dimensional Cartesian point indexer using `core.py`.
- `closest_point(point)` — returns the closest Cartesian point in the tree.
- `closest_point_per_quadrant(point)` — returns a dictionary of closest points per quadrant (`ne`, `nw`, `se`, `sw`) for 2D points.

**`geokdtree/core.py`** — pure Python KD-Tree primitives:
- `kdtree(points, depth, axis_count)` — recursively partitions points along cycling axes by finding the median ($O(N \log N)$ construction).
- `closest_point(node, point, best, axis_count, best_dist)` — recursive branch and bound nearest neighbor search ($O(\log N)$ query).
- `closest_point_per_quadrant_2d(node, point)` — recursive nearest neighbor search across all 4 quadrants for 2D points.
- `squared_distance(p1, p2, axis_count)` — Euclidean squared distance across $N$ dimensions.

**`geokdtree/cpp/`** — C++ acceleration (`nanobind`):
- High-performance C++20 KD-Tree and spherical spatial index.
- Provides `geokdtree.cpp.GeoKDTree` and `geokdtree.cpp.KDTree`.
- Achieves ~10x–20x faster query lookups and ~1.5x faster tree construction.

---

## Environment Variables

| Variable | Purpose |
|---|---|
| `GEOKDTREE_REQUIRE_CPP=1` | Test / runtime flag requiring the C++ extension to be loaded (asserts `geokdtree.cpp` is used). |
| `GEOKDTREE_REQUIRE_PYTHON=1` | Test / runtime flag requiring the pure Python fallback to be loaded (asserts `geokdtree.geokdtree` is used). |
| `GEOKDTREE_NO_BUILD=1` | Instructs `scikit-build-core` to skip CMake compilation, installing in pure Python mode. |

---

## Coding Conventions

- **Line length**: 80 characters (`black` config in `pyproject.toml`).
- **Python version**: ≥ 3.11 (`str | None` union syntax, `tuple[float, float]` type annotations).
- **Zero runtime dependencies**: Pure Python fallback must use only Python standard library (`math`, `random`, `time`).
- **No unnecessary abstractions**: Keep spatial operations direct and performant.
- **DO NOT generate docs**: Only the maintainer generates docs at release time.

---

Python: **≥ 3.11** | Zero Runtime Dependencies
