import pytest
import geokdtree
from geokdtree.kdtree import KDTree as PyKDTree

try:
    from geokdtree.cpp import KDTree as CppKDTree
except ImportError:
    CppKDTree = None

IMPLEMENTATIONS = [geokdtree.KDTree, PyKDTree]
if CppKDTree is not None and CppKDTree not in IMPLEMENTATIONS:
    IMPLEMENTATIONS.append(CppKDTree)


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_kdtree_2d_basic(TreeClass):
    points = [(0, 0), (5, 5), (10, 10), (1, 2)]
    tree = TreeClass(points)

    # Exact matches
    assert tree.closest_point((0, 0)) == (0, 0)
    assert tree.closest_point((5, 5)) == (5, 5)
    assert tree.closest_point((10, 10)) == (10, 10)
    assert tree.closest_point((1, 2)) == (1, 2)

    # Proximity queries
    assert tree.closest_point((1, 1)) == (1, 2)
    assert tree.closest_point((9, 9)) == (10, 10)
    assert tree.closest_point((4, 6)) == (5, 5)


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_kdtree_1d(TreeClass):
    points = [(1,), (5,), (10,), (20,)]
    tree = TreeClass(points)
    assert tree.closest_point((6,)) == (5,)
    assert tree.closest_point((18,)) == (20,)
    assert tree.closest_point((0,)) == (1,)


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_kdtree_3d(TreeClass):
    points = [(0, 0, 0), (10, 10, 10), (5, 5, 5)]
    tree = TreeClass(points)
    assert tree.closest_point((4, 4, 4)) == (5, 5, 5)
    assert tree.closest_point((9, 10, 9)) == (10, 10, 10)
    assert tree.closest_point((-1, 0, 1)) == (0, 0, 0)


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_kdtree_4d(TreeClass):
    points = [(0, 0, 0, 0), (1, 1, 1, 1), (5, 5, 5, 5)]
    tree = TreeClass(points)
    assert tree.closest_point((1.1, 0.9, 1.0, 1.0)) == (1, 1, 1, 1)
    assert tree.closest_point((4.8, 5.1, 5.0, 4.9)) == (5, 5, 5, 5)


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_kdtree_single_point(TreeClass):
    tree = TreeClass([(42, 42)])
    assert tree.closest_point((100, 100)) == (42, 42)
    assert tree.closest_point((0, 0)) == (42, 42)


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_kdtree_scale_correctness(TreeClass):
    points = [(i, i + 1) for i in range(100)]
    tree = TreeClass(points)
    assert tree.closest_point((5, 5.5)) == (5, 6)
    assert tree.closest_point((50, 51)) == (50, 51)
    assert tree.closest_point((99, 100)) == (99, 100)


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_kdtree_closest_point_per_quadrant(TreeClass):
    points = [
        (2.0, 2.0),
        (-2.0, 2.0),
        (2.0, -2.0),
        (-2.0, -2.0),
        (5.0, 5.0),
    ]
    tree = TreeClass(points)
    quads = tree.closest_point_per_quadrant((0.0, 0.0))

    assert quads["ne"] == (2.0, 2.0)
    assert quads["nw"] == (-2.0, 2.0)
    assert quads["se"] == (2.0, -2.0)
    assert quads["sw"] == (-2.0, -2.0)


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_kdtree_closest_point_per_quadrant_partial(TreeClass):
    # Only points in NE and SE
    points = [(3.0, 4.0), (3.0, -4.0)]
    tree = TreeClass(points)
    quads = tree.closest_point_per_quadrant((0.0, 0.0))

    assert quads["ne"] == (3.0, 4.0)
    assert quads["se"] == (3.0, -4.0)
    assert quads["nw"] is None
    assert quads["sw"] is None


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_kdtree_closest_point_per_quadrant_error_on_3d(TreeClass):
    points = [(1, 2, 3), (4, 5, 6)]
    tree = TreeClass(points)
    with pytest.raises((ValueError, Exception)):
        tree.closest_point_per_quadrant((0, 0, 0))
