from geokdtree.core import (
    kdtree,
    squared_distance,
    closest_point,
    closest_point_per_quadrant_2d,
)


def test_core_squared_distance():
    assert squared_distance((0, 0), (3, 4), axis_count=2) == 25
    assert squared_distance((1, 2, 3), (4, 6, 8), axis_count=3) == 50
    assert squared_distance((0, 0, 0, 0), (1, 1, 1, 1), axis_count=4) == 4


def test_core_kdtree_empty():
    assert kdtree([], depth=0, axis_count=2) == 0


def test_core_kdtree_build():
    points = [(1, 2), (3, 4), (5, 6)]
    tree = kdtree(points, depth=0, axis_count=2)
    assert tree[0] == (3, 4)
    assert tree[1] == 0
    # Left child
    assert tree[2][0] == (1, 2)
    # Right child
    assert tree[3][0] == (5, 6)


def test_core_closest_point():
    points = [(1, 2), (3, 4), (5, 6)]
    tree = kdtree(points, depth=0, axis_count=2)
    best_point, best_dist = closest_point(tree, (2.5, 3.5), axis_count=2)
    assert best_point == (3, 4)
    assert best_dist == 0.5


def test_core_closest_point_empty():
    best_point, best_dist = closest_point(0, (1, 1))
    assert best_point is None
    assert best_dist == float("inf")


def test_core_closest_point_per_quadrant_2d():
    points = [(10, 10), (-10, 10), (10, -10), (-10, -10)]
    tree = kdtree(points, depth=0, axis_count=2)
    quads = closest_point_per_quadrant_2d(tree, (0, 0))
    assert quads["ne"] == (10, 10)
    assert quads["nw"] == (-10, 10)
    assert quads["se"] == (10, -10)
    assert quads["sw"] == (-10, -10)
