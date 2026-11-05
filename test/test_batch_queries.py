"""Batch searches preserve scalar behavior and the original query order."""

import random

import pytest

from geokdtree.kdtree import KDTree as PyKDTree
from geokdtree.geokdtree import GeoKDTree as PyGeoKDTree

KD_CLASSES = [PyKDTree]
GEO_CLASSES = [PyGeoKDTree]
try:
    from geokdtree.cpp import KDTree, GeoKDTree

    KD_CLASSES.append(KDTree)
    GEO_CLASSES.append(GeoKDTree)
except ImportError:
    pass


@pytest.mark.parametrize("cls", KD_CLASSES)
@pytest.mark.parametrize("dimensions", [1, 2, 3, 7, 17])
def test_cartesian_batch_matches_scalar_and_brute_force(cls, dimensions):
    rng = random.Random(481 + dimensions)
    points = [
        tuple(rng.uniform(-10, 10) for _ in range(dimensions))
        for _ in range(51)
    ]
    points += points[:3]
    tree = cls(points.copy())
    queries = [
        tuple(rng.uniform(-30, 30) for _ in range(dimensions))
        for _ in range(23)
    ]
    queries += [points[4], points[0], points[4]]
    saved = queries.copy()
    results = tree.closest_points(queries)
    assert queries == saved
    assert results == [tree.closest_point(q) for q in queries]
    for query, result in zip(queries, results):
        distance = lambda p: sum((x - y) ** 2 for x, y in zip(query, p))
        assert distance(result) == min(map(distance, points))
    assert results[-3] == results[-1] == points[4]
    assert tree.closest_points([]) == []


@pytest.mark.parametrize("cls", GEO_CLASSES)
def test_geographic_batches_original_indices_and_scalar_parity(cls):
    points = [
        (90.0, 0.0),
        (-90.0, 45.0),
        (0.0, -179.99),
        (0.0, 179.99),
        (34.0522, -118.2437),
        (40.7128, -74.0060),
        (0.0, 179.99),
    ]
    queries = [
        (47.6, -122.3),
        (0.0, 180.0),
        (89.0, -120.0),
        (-89.0, 20.0),
        (41.0, -74.0),
        (0.0, -180.0),
        (47.6, -122.3),
    ]
    saved = points.copy()
    tree = cls(points)
    indices = tree.closest_indices(queries)
    assert indices == [tree.closest_idx(q) for q in queries]
    assert tree.closest_points(queries) == [points[i] for i in indices]
    assert tree.closest_points(queries) == [
        tree.closest_point(q) for q in queries
    ]
    assert indices[0] == indices[-1] == 4
    assert points == saved
    assert tree.closest_points([]) == []
    assert tree.closest_indices([]) == []


@pytest.mark.parametrize("cls", KD_CLASSES + GEO_CLASSES)
def test_batches_accept_iterables_and_have_no_cross_call_state(cls):
    points = [(0.0, 0.0), (3.0, 5.0), (-4.0, -1.0)]
    tree = cls(points.copy())
    queries = [points[2], points[0], points[1], points[2]]
    assert tree.closest_points(iter(queries)) == queries
    assert tree.closest_points(tuple(queries)) == queries
    assert tree.closest_points(reversed(queries)) == list(reversed(queries))
    assert tree.closest_points(queries) == queries
    assert tree.closest_points(points=queries) == queries
    if cls in GEO_CLASSES:
        assert tree.closest_indices(iter(queries)) == [2, 0, 1, 2]
        assert tree.closest_indices(points=queries) == [2, 0, 1, 2]
        assert tree.closest_indicies(queries) == [2, 0, 1, 2]
        assert tree.closest_indicies(points=queries) == [2, 0, 1, 2]


@pytest.mark.parametrize("cls", KD_CLASSES + GEO_CLASSES)
@pytest.mark.parametrize(
    "query",
    [
        (1.0,),
        (1.0, 2.0, 3.0),
        (float("nan"), 1.0),
        (1.0, float("inf")),
        (-float("inf"), 0.0),
    ],
)
def test_invalid_batch_coordinates(cls, query):
    tree = cls([(0.0, 0.0)])
    methods = [tree.closest_points]
    if cls in GEO_CLASSES:
        methods.append(tree.closest_indices)
    for method in methods:
        with pytest.raises(ValueError):
            method([(0.0, 0.0), query])


@pytest.mark.parametrize("cls", [PyKDTree, PyGeoKDTree])
def test_python_empty_tree_batch(cls):
    tree = cls([])
    assert tree.closest_points([]) == []
    with pytest.raises(ValueError):
        tree.closest_points([(0.0, 0.0)])
    if cls is PyGeoKDTree:
        assert tree.closest_indices([]) == []
        with pytest.raises(ValueError):
            tree.closest_indices([(0.0, 0.0)])


@pytest.mark.parametrize(
    "cls",
    [c for c in KD_CLASSES + GEO_CLASSES if c.__module__ == "geokdtree.cpp"],
)
def test_native_legacy_empty_constructor(cls):
    with pytest.raises(ValueError):
        cls([])


@pytest.mark.parametrize("cls", KD_CLASSES + GEO_CLASSES)
def test_batch_api_has_no_order_or_hilbert_constructor_options(cls):
    points = [(0.0, 0.0)]
    for option in [
        {"hilbert": True},
        {"hilbert_bits": 16},
        {"hilbert_search": "jump"},
    ]:
        with pytest.raises(TypeError):
            cls(points.copy(), **option)
    tree = cls(points.copy())
    with pytest.raises(TypeError):
        tree.closest_points([], order="input")
    if cls in GEO_CLASSES:
        with pytest.raises(TypeError):
            tree.closest_indices([], order="input")
