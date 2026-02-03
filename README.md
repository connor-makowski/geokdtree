# GeoKDTree
[![PyPI version](https://badge.fury.io/py/geokdtree.svg)](https://badge.fury.io/py/geokdtree)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Downloads](https://pepy.tech/badge/geokdtree)](https://pypi.org/project/geokdtree/)
<!-- [![PyPI Downloads](https://img.shields.io/pypi/dm/geokdtree.svg?label=PyPI%20downloads)](https://pypi.org/project/geokdtree/) -->


### A Geo KD Tree package for Python


![geokdtree](https://raw.githubusercontent.com/connor-makowski/geokdtree/main/static/geokdtree.png)

## Quick Start:
```py
from geokdtree import GeoKDTree

example_points = [
    (34.0522, -118.2437),  # Los Angeles
    (40.7128, -74.0060),   # New York
    (37.7749, -122.4194),  # San Francisco
    (51.5074, -0.1278),    # London
    (48.8566, 2.3522),     # Paris
]

geo_kd_tree = GeoKDTree(points = example_points)
test_point = (47.6062, -122.3321) # Seattle

closest_idx = geo_kd_tree.closest_idx(test_point) # Expect San Francisco to be closest
print(f"Closest point to {test_point} is {example_points[closest_idx] }")
```

### Documentation

- Docs: https://connor-makowski.github.io/geokdtree/geokdtree.html
- Git Repo: https://github.com/connor-makowski/geokdtree

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

