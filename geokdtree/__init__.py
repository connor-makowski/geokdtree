"""
# GeoKDTree
[![PyPI version](https://badge.fury.io/py/geokdtree.svg)](https://badge.fury.io/py/geokdtree)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Downloads](https://pepy.tech/badge/geokdtree)](https://pypi.org/project/geokdtree/)
<!-- [![PyPI Downloads](https://img.shields.io/pypi/dm/geokdtree.svg?label=PyPI%20downloads)](https://pypi.org/project/geokdtree/) -->

# GeoKDTree

## Ultra-fast nearest-neighbor lookup for latitude/longitude data

**GeoKDTree** is a lightweight, high-performance spatial indexing library for Python designed to find the *nearest geographic coordinate* from massive datasets in nanoseconds.

It wraps a highly optimized KD-Tree with a geographic interface, allowing you to work directly with `(latitude, longitude)` pairs. No projections, no external dependencies, and no heavy GIS stacks.

![geokdtree](https://raw.githubusercontent.com/connor-makowski/geokdtree/main/static/geokdtree.png)

### Documentation

- Docs: https://connor-makowski.github.io/geokdtree/geokdtree.html
- Git Repo: https://github.com/connor-makowski/geokdtree

## Installation

```bash
pip install geokdtree
```

## Getting Started

```python
from geokdtree import GeoKDTree

example_points = [
    (34.0522, -118.2437),  # Los Angeles
    (40.7128, -74.0060),   # New York
    (37.7749, -122.4194),  # San Francisco
    (51.5074, -0.1278),    # London
    (48.8566, 2.3522),     # Paris
]

geo_kd_tree = GeoKDTree(points=example_points)

test_point = (47.6062, -122.3321)  # Seattle
# Find the index of the closest point in the original dataset
closest_idx = geo_kd_tree.closest_idx(test_point)
# Find the closest point itself
closest_point = geo_kd_tree.closest_point(test_point)

print(f"Closest index (from original data) is {closest_idx}")
print(f"Closest point (from original data) is {closest_point}")
```

## Why Use GeoKDTree?

GeoKDTree is designed to solve one focused problem extremely well:

**Fast nearest-neighbor lookup for latitude/longitude data at scale.**

It is worth noting that the closest point found may not be the true closest point, but should be very close for most practical applications. See KD-Tree limitations for more details.

### Extremely Fast Lookups

Once constructed, nearest-neighbor queries consistently complete in **tens of nanoseconds**, even with very large datasets.

Typical benchmark results from the included tests:

| Number of Points | Build Time | Query Time |
| ---------------: | ---------: | ---------: |
|            1,000 |    ~1.7 ms |   ~0.02 ms |
|           10,000 |     ~25 ms |   ~0.05 ms |
|          100,000 |    ~350 ms |   ~0.05 ms |
|        1,000,000 |     ~6.8 s |   ~0.07 ms |

This makes GeoKDTree well-suited for:

* Real-time proximity queries
* Matching incoming coordinates against large reference datasets
* High-throughput geospatial APIs
* Pre-filtering before more expensive geospatial calculations

> Exact timings depend on hardware, Python version, and data distribution. These values reflect typical results from the repository’s benchmarks.

### Built for Geographic Coordinates

GeoKDTree works directly with `(latitude, longitude)` pairs.

You do **not** need to:

* Project coordinates into planar space
* Use heavyweight GIS libraries
* Maintain custom spatial indexing code

Just pass geographic coordinates and query.

### Simple API, Minimal Overhead

GeoKDTree intentionally keeps the API small and focused.

* Build once from a list of coordinates
* Query nearest neighbors with a single method call
* Retrieve indices or points directly from your original dataset

There are no external C extensions or heavy dependencies, keeping installation and deployment simple.

### Deterministic and Predictable Performance

* Tree construction scales at approximately `O(n log n)`
* Query performance scales at approximately `O(log n)`
* No probabilistic approximations
* No background indexing or caching

This predictability is valuable for production systems where latency and reproducibility matter.

## Supported Features

See: https://connor-makowski.github.io/geokdtree/geokdtree.html

## Contributing

Issues, feature requests, and pull requests are welcome.
Please open an issue to discuss changes or enhancements.

# Development
## Running Tests, Prettifying Code, and Updating Docs

Make sure Docker is installed and running on a Unix system (Linux, MacOS, WSL2).

- Create a docker container and drop into a shell
    - `./run.sh`
- Run all tests (see ./utils/test.sh)
    - `./run.sh test`
- Prettify the code (see ./utils/prettify.sh)
    - `./run.sh prettify`
- Update the docs (see ./utils/docs.sh)
    - `./run.sh docs`

- Note: You can and should modify the `Dockerfile` to test different python versions.

"""

from .geokdtree import GeoKDTree
from .kdtree import KDTree
