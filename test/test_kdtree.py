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


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_kdtree_batch_queries_2d(TreeClass):
    points = [(0.0, 0.0), (10.0, 10.0), (5.0, 5.0)]
    tree = TreeClass(points)
    queries = [(1.0, 1.0), (9.0, 9.0), (4.0, 6.0)]
    expected = [(0.0, 0.0), (10.0, 10.0), (5.0, 5.0)]
    assert tree.closest_points(queries) == expected
    # Generator support
    assert tree.closest_points(q for q in queries) == expected
    # Empty batch
    assert tree.closest_points([]) == []


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_kdtree_batch_queries_nd(TreeClass):
    # 1D
    t1 = TreeClass([(1.0,), (5.0,), (10.0,)])
    assert t1.closest_points([(2.0,), (8.0,)]) == [(1.0,), (10.0,)]
    assert t1.closest_points([]) == []

    # 3D
    t3 = TreeClass([(0.0, 0.0, 0.0), (10.0, 10.0, 10.0)])
    assert t3.closest_points([(1.0, 1.0, 1.0), (9.0, 9.0, 9.0)]) == [
        (0.0, 0.0, 0.0),
        (10.0, 10.0, 10.0),
    ]


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_kdtree_batch_validation_errors(TreeClass):
    tree = TreeClass([(0.0, 0.0), (1.0, 1.0)])
    # Wrong dimension
    with pytest.raises((ValueError, TypeError)):
        tree.closest_points([(1.0,)])
    with pytest.raises((ValueError, TypeError)):
        tree.closest_points([(1.0, 2.0, 3.0)])
    # Non-finite coordinates
    with pytest.raises((ValueError, TypeError)):
        tree.closest_points([(1.0, float("nan"))])
    with pytest.raises((ValueError, TypeError)):
        tree.closest_points([(float("inf"), 1.0)])

    # Integer overflow in batch conversion
    with pytest.raises((OverflowError, ValueError)):
        tree.closest_points([(10**1000, 1.0)])

    # Late invalid item in generator
    def gen_with_bad_tail():
        yield (0.5, 0.5)
        yield (1.0, float("nan"))

    with pytest.raises((ValueError, TypeError)):
        tree.closest_points(gen_with_bad_tail())


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_kdtree_tie_breaking_and_duplicates(TreeClass):
    # Multiple points with identical distances: deterministic root median winner
    points = [(1.0, 0.0, 0.0), (-1.0, 0.0, 0.0)]
    tree = TreeClass(points)
    assert tree.closest_point((0.0, 0.0, 0.0)) == (1.0, 0.0, 0.0)

    # 1D ties
    t1 = TreeClass([(1.0,), (-1.0,)])
    assert t1.closest_point((0.0,)) == (1.0,)

    # 2D ties
    t2 = TreeClass([(1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)])
    assert t2.closest_point((0.0, 0.0)) in [
        (1.0, 0.0),
        (-1.0, 0.0),
        (0.0, 1.0),
        (0.0, -1.0),
    ]

    # 7D ties
    p7_pos = (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    p7_neg = (-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    t7 = TreeClass([p7_pos, p7_neg])
    assert t7.closest_point((0.0,) * 7) == p7_pos

    # Duplicate coordinates in dataset
    dup_points = [
        (2.0, 3.0, 4.0),
        (0.0, 0.0, 0.0),
        (2.0, 3.0, 4.0),
        (-1.0, -1.0, -1.0),
    ]
    dup_tree = TreeClass(dup_points)
    assert dup_tree.closest_point((2.0, 3.0, 4.0)) == (2.0, 3.0, 4.0)
    assert dup_tree.closest_point((2.0, 3.0, 4.1)) == (2.0, 3.0, 4.0)
    assert dup_tree.closest_points([(2.0, 3.0, 4.0), (-1.0, -1.0, -1.0)]) == [
        (2.0, 3.0, 4.0),
        (-1.0, -1.0, -1.0),
    ]


class CustomFloat(float):
    pass


class CustomInt(int):
    pass


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_kdtree_numeric_subclasses_and_overflow(TreeClass):
    # Custom numeric subclasses work transparently
    pts = [(CustomFloat(1.0), CustomInt(2)), (CustomFloat(3.0), CustomInt(4))]
    tree = TreeClass(pts)
    assert tree.closest_point((CustomFloat(1.1), CustomInt(2))) == (1.0, 2.0)
    assert tree.closest_points([(CustomFloat(1.1), CustomInt(2))]) == [
        (1.0, 2.0)
    ]

    # Batch overflow is validated on both backends via math.isfinite / extract_double
    with pytest.raises((OverflowError, ValueError)):
        tree.closest_points([(10**1000, 1.0)])

    # C++ native type conversions require coordinates to fit in double
    if "geokdtree.cpp" in TreeClass.__module__:
        # Overflow in construction
        with pytest.raises((OverflowError, ValueError)):
            TreeClass([(10**1000, 1.0)])

        # Overflow in scalar query
        t2 = TreeClass([(0.0, 0.0)])
        with pytest.raises((OverflowError, ValueError)):
            t2.closest_point((10**1000, 1.0))

        # Overflow in 3D query
        t3 = TreeClass([(0.0, 0.0, 0.0)])
        with pytest.raises((OverflowError, ValueError)):
            t3.closest_point((10**1000, 1.0, 2.0))


class CustomFloatProto:
    def __init__(self, v):
        self.v = v

    def __float__(self):
        return float(self.v)


class FailingFloatProto:
    def __float__(self):
        raise ValueError("failing float conversion")


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_kdtree_decimal_and_custom_float_protocols(TreeClass):
    import decimal

    points_3d = [(0.0, 0.0, 0.0), (10.0, 10.0, 10.0)]
    tree_3d = TreeClass(points_3d)

    q_bool = (True, False, 1.0)
    assert tree_3d.closest_point(q_bool) == (0.0, 0.0, 0.0)
    assert tree_3d.closest_points([q_bool]) == [(0.0, 0.0, 0.0)]

    # C++ converts custom numeric objects with __float__ or Decimal
    if "geokdtree.cpp" in TreeClass.__module__:
        q_dec = (
            decimal.Decimal("1.0"),
            decimal.Decimal("2.0"),
            decimal.Decimal("3.0"),
        )
        assert tree_3d.closest_point(q_dec) == (0.0, 0.0, 0.0)
        assert tree_3d.closest_points([q_dec]) == [(0.0, 0.0, 0.0)]

        q_proto = (
            CustomFloatProto(1.0),
            CustomFloatProto(2.0),
            CustomFloatProto(3.0),
        )
        assert tree_3d.closest_point(q_proto) == (0.0, 0.0, 0.0)
        assert tree_3d.closest_points([q_proto]) == [(0.0, 0.0, 0.0)]

        # Failing __float__ propagates custom exception
        with pytest.raises(ValueError, match="failing float conversion"):
            tree_3d.closest_point((FailingFloatProto(), 0.0, 0.0))

    # Strings raise TypeError
    with pytest.raises((TypeError, ValueError)):
        tree_3d.closest_point(("invalid_coord", 0.0, 0.0))
    with pytest.raises((TypeError, ValueError)):
        tree_3d.closest_points([("invalid_coord", 0.0, 0.0)])


@pytest.mark.parametrize("TreeClass", IMPLEMENTATIONS)
def test_kdtree_7d_queries_and_batch(TreeClass):
    import random

    rng = random.Random(42)
    pts_7d = [tuple(rng.random() for _ in range(7)) for _ in range(50)]
    tree_7d = TreeClass(pts_7d)

    # Exact match queries
    for pt in pts_7d[:5]:
        assert tree_7d.closest_point(pt) == pt

    # Offset queries
    queries = [tuple(rng.random() for _ in range(7)) for _ in range(10)]
    scalar_results = [tree_7d.closest_point(q) for q in queries]
    batch_results = tree_7d.closest_points(queries)

    assert len(batch_results) == len(queries)
    for s, b in zip(scalar_results, batch_results):
        assert s == b
        assert s in pts_7d

    # Dimension mismatch
    with pytest.raises((ValueError, TypeError, IndexError)):
        tree_7d.closest_point((0.5, 0.5, 0.5))
    with pytest.raises((ValueError, TypeError)):
        tree_7d.closest_points([(0.5, 0.5, 0.5)])
