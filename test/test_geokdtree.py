import pytest
import math
import geokdtree
from geokdtree.geokdtree import (
    GeoKDTree as PyGeoKDTree,
    __lat_lon_idx_to_xyz_idx__ as py_lat_lon_to_xyz,
)

try:
    from geokdtree.cpp import GeoKDTree as CppGeoKDTree
except ImportError:
    CppGeoKDTree = None

IMPLEMENTATIONS = [geokdtree.GeoKDTree, PyGeoKDTree]
if CppGeoKDTree is not None and CppGeoKDTree not in IMPLEMENTATIONS:
    IMPLEMENTATIONS.append(CppGeoKDTree)

EXAMPLE_POINTS = [
    (34.0522, -118.2437),  # 0: Los Angeles
    (40.7128, -74.0060),  # 1: New York
    (37.7749, -122.4194),  # 2: San Francisco
    (51.5074, -0.1278),  # 3: London
    (48.8566, 2.3522),  # 4: Paris
]


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_geokdtree_basic_cities(TreeClass):
    tree = TreeClass(EXAMPLE_POINTS)

    # Query Seattle -> San Francisco (idx 2)
    seattle = (47.6062, -122.3321)
    assert tree.closest_idx(seattle) == 2
    assert tree.closest_point(seattle) == EXAMPLE_POINTS[2]

    # Query Oxford -> London (idx 3)
    oxford = (51.7520, -1.2577)
    assert tree.closest_idx(oxford) == 3
    assert tree.closest_point(oxford) == EXAMPLE_POINTS[3]

    # Query Lyon -> Paris (idx 4)
    lyon = (45.7640, 4.8357)
    assert tree.closest_idx(lyon) == 4
    assert tree.closest_point(lyon) == EXAMPLE_POINTS[4]

    # Query Boston -> New York (idx 1)
    boston = (42.3601, -71.0589)
    assert tree.closest_idx(boston) == 1
    assert tree.closest_point(boston) == EXAMPLE_POINTS[1]

    # Query San Diego -> Los Angeles (idx 0)
    san_diego = (32.7157, -117.1611)
    assert tree.closest_idx(san_diego) == 0
    assert tree.closest_point(san_diego) == EXAMPLE_POINTS[0]


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_geokdtree_exact_matches(TreeClass):
    tree = TreeClass(EXAMPLE_POINTS)
    for idx, pt in enumerate(EXAMPLE_POINTS):
        assert tree.closest_idx(pt) == idx
        assert tree.closest_point(pt) == pt


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_geokdtree_consistency(TreeClass):
    tree = TreeClass(EXAMPLE_POINTS)
    test_queries = [
        (0.0, 0.0),
        (45.0, -100.0),
        (55.0, 10.0),
        (-20.0, -50.0),
        (80.0, 0.0),
    ]
    for q in test_queries:
        idx = tree.closest_idx(q)
        pt = tree.closest_point(q)
        assert pt == EXAMPLE_POINTS[idx]


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_geokdtree_poles_and_equator(TreeClass):
    points = [
        (90.0, 0.0),  # North Pole
        (-90.0, 0.0),  # South Pole
        (0.0, 0.0),  # Equator / Prime Meridian
        (0.0, 180.0),  # Equator / Antimeridian
    ]
    tree = TreeClass(points)

    assert tree.closest_idx((85.0, 45.0)) == 0
    assert tree.closest_point((85.0, 45.0)) == (90.0, 0.0)

    assert tree.closest_idx((-85.0, -45.0)) == 1
    assert tree.closest_point((-85.0, -45.0)) == (-90.0, 0.0)

    assert tree.closest_idx((1.0, 1.0)) == 2
    assert tree.closest_point((1.0, 1.0)) == (0.0, 0.0)


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_geokdtree_single_point(TreeClass):
    point = (37.7749, -122.4194)
    tree = TreeClass([point])
    assert tree.closest_idx((0, 0)) == 0
    assert tree.closest_point((0, 0)) == point


def test_lat_lon_to_xyz_conversion():
    x, y, z, idx = py_lat_lon_to_xyz(0, 0, 5)
    assert math.isclose(x, 1.0, abs_tol=1e-6)
    assert math.isclose(y, 0.0, abs_tol=1e-6)
    assert math.isclose(z, 0.0, abs_tol=1e-6)
    assert idx == 5

    x, y, z, idx = py_lat_lon_to_xyz(90, 0, 1)
    assert math.isclose(x, 0.0, abs_tol=1e-6)
    assert math.isclose(y, 0.0, abs_tol=1e-6)
    assert math.isclose(z, 1.0, abs_tol=1e-6)
    assert idx == 1

    x, y, z, idx = py_lat_lon_to_xyz(0, 90, 2)
    assert math.isclose(x, 0.0, abs_tol=1e-6)
    assert math.isclose(y, 1.0, abs_tol=1e-6)
    assert math.isclose(z, 0.0, abs_tol=1e-6)
    assert idx == 2
