r"""
# GeoKDTree
[![PyPI version](https://badge.fury.io/py/geokdtree.svg)](https://badge.fury.io/py/geokdtree)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Downloads](https://pepy.tech/badge/geokdtree)](https://pypi.org/project/geokdtree/)
<!-- [![PyPI Downloads](https://img.shields.io/pypi/dm/geokdtree.svg?label=PyPI%20downloads)](https://pypi.org/project/geokdtree/) -->

## Ultra-fast nearest-neighbor lookup for latitude/longitude data

**GeoKDTree** is a lightweight, high-performance spatial indexing library for Python designed to find the *nearest geographic coordinate* from massive datasets in nanoseconds.

It wraps a highly optimized KD-Tree with a geographic interface, allowing you to work directly with `(latitude, longitude)` pairs. No projections, no external dependencies, and no heavy GIS stacks.

![geokdtree](https://raw.githubusercontent.com/connor-makowski/geokdtree/main/static/geokdtree.png)

### Documentation

- Docs: https://connor-makowski.github.io/geokdtree/geokdtree.html
- Git Repo: https://github.com/connor-makowski/geokdtree

## Installation

### Standard Installation (with C++ acceleration)

```bash
pip install geokdtree
```

### Pure Python Installation (Skip Binary Builds)

If you want to install `geokdtree` in pure Python mode without compiling or using binary extensions (or in environments without a C++ compiler):

- **Linux / macOS / WSL2**:
  ```bash
  GEOKDTREE_NO_BUILD=1 pip install --no-binary geokdtree geokdtree
  ```
  Or with `uv`:
  ```bash
  GEOKDTREE_NO_BUILD=1 uv pip install --no-binary geokdtree geokdtree
  ```

- **Windows (PowerShell)**:
  ```powershell
  $env:GEOKDTREE_NO_BUILD="1"
  pip install --no-binary geokdtree geokdtree
  ```

- **Windows (CMD)**:
  ```cmd
  set GEOKDTREE_NO_BUILD=1
  pip install --no-binary geokdtree geokdtree
  ```

#### Automatic Fallback
When building from source, if a C++ compiler is not available or compilation fails, `geokdtree` will automatically fall back to the pure Python implementation.

## Getting Started

```python
from geokdtree import GeoKDTree

example_points = [
    (34.0522, -118.2437),  # Los Angeles
    (40.7128, -74.0060),  # New York
    (37.7749, -122.4194),  # San Francisco
    (51.5074, -0.1278),  # London
    (48.8566, 2.3522),  # Paris
]

geo_kd_tree = GeoKDTree(points=example_points)

test_point = (47.6062, -122.3321)  # Seattle
# Find the index of the closest point in the original dataset
closest_idx = geo_kd_tree.closest_idx(test_point)  # => 2
# Find the closest point itself
closest_point = geo_kd_tree.closest_point(test_point)  # => (37.7749, -122.4194)

# Find closest points in each quadrant (ne, nw, se, sw)
quadrants = geo_kd_tree.closest_point_per_quadrant(test_point)
# => {'ne': (51.5074, -0.1278), 'nw': None, 'se': (40.7128, -74.006), 'sw': (37.7749, -122.4194)}
```

## Why Use GeoKDTree?

GeoKDTree is designed to solve one focused problem extremely well:

**Fast nearest-neighbor lookup for latitude/longitude data at scale.**

It is worth noting that the closest point found may not be the true closest point, but should be very close for most practical applications. See KD-Tree limitations for more details.

### Extremely Fast Lookups

Once constructed, nearest-neighbor queries consistently complete in **hundreds of nanoseconds to single-digit microseconds**, even with 1,000,000 coordinates.

Typical benchmark results (see [benchmark.md](benchmark.md) for full benchmarks):

| Number of Points ($N$) | C++ Build Time | Python Build Time | C++ Query Time | Python Query Time | Query Speedup |
| ---------------------: | -------------: | ----------------: | -------------: | ----------------: | ------------: |
|                  1,000 |        ~1.1 ms |           ~1.6 ms |       ~0.65 µs |          ~12.5 µs |          ~19x |
|                 10,000 |         ~15 ms |            ~21 ms |       ~0.85 µs |          ~16.1 µs |          ~19x |
|                100,000 |        ~225 ms |           ~350 ms |        ~1.8 µs |          ~24.0 µs |          ~13x |
|              1,000,000 |         ~3.8 s |            ~6.3 s |        ~3.2 µs |          ~31.5 µs |          ~10x |

This makes GeoKDTree well-suited for:

* Real-time proximity queries
* Matching incoming coordinates against large reference datasets
* High-throughput geospatial APIs
* Pre-filtering before more expensive geospatial calculations

> Exact timings depend on hardware, Python version, and data distribution. These values reflect typical results from `utils/benchmark.py`.

### Built for Geographic Coordinates

GeoKDTree works directly with `(latitude, longitude)` pairs.

You do **not** need to:

* Project coordinates into planar space
* Use heavyweight GIS libraries
* Maintain custom spatial indexing code

Just pass geographic coordinates and query.

### Simple API, Zero Runtime Dependencies

GeoKDTree intentionally keeps the API small and focused.

* Build once from a list of coordinates
* Query nearest neighbors with a single method call
* Retrieve indices or points directly from your original dataset
* Zero external runtime dependencies, with optional C++ acceleration via `nanobind` and automatic pure Python fallback.

### Deterministic and Predictable Performance

* Tree construction scales at approximately $O(N \log N)$
* Query performance scales at approximately $O(\log N)$
* No probabilistic approximations
* No background indexing or caching

This predictability is valuable for production systems where latency and reproducibility matter.

## Supported Features

See: https://connor-makowski.github.io/geokdtree/geokdtree.html

## Contributing

Issues, feature requests, and pull requests are welcome.
Please open an issue to discuss changes or enhancements.

## Development

### Setup & Testing

1. Clone the repository and install development dependencies:
   ```bash
   uv sync --extra dev --reinstall-package geokdtree
   ```

2. Run the test suite:
   ```bash
   uv run pytest
   ```

3. Run full test matrix across Python versions (3.11–3.14 & PyPy3.11):
   ```bash
   uv run nox
   ```

4. Run performance benchmarks:
   ```bash
   uv run python utils/benchmark.py
   ```

5. Prettify and format code:
   ```bash
   uv run python utils/prettify.py
   ```

"""

import os

if os.environ.get("GEOKDTREE_REQUIRE_PYTHON") == "1":
    from geokdtree.geokdtree import GeoKDTree
    from geokdtree.kdtree import KDTree
else:
    try:
        from geokdtree.cpp import GeoKDTree, KDTree
    except ImportError:
        from geokdtree.geokdtree import GeoKDTree
        from geokdtree.kdtree import KDTree
