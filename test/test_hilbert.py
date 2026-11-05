"""Integer orientation, exact normalization, and stable ordering contracts."""

import itertools
import math
import random

import pytest

from geokdtree import GeoHilbert, Hilbert
from geokdtree.hilbert import (
    GeoHilbert as PyGeoHilbert,
    _quantize,
    hilbert_coordinates,
    hilbert_index,
    hilbert_order,
)

try:
    from geokdtree.cpp import hilbert_index as native_index
    from geokdtree.cpp import hilbert_coordinates as native_coordinates
except ImportError:
    native_index = native_coordinates = None


@pytest.mark.parametrize(
    "dimensions,bits", [(1, 5), (2, 1), (2, 3), (3, 2), (4, 2)]
)
def test_exhaustive_grids(dimensions, bits):
    points = [
        hilbert_coordinates(i, dimensions=dimensions, bits=bits)
        for i in range(1 << (dimensions * bits))
    ]
    assert len(set(points)) == len(points)
    assert set(points) == set(
        itertools.product(range(1 << bits), repeat=dimensions)
    )
    for i, point in enumerate(points):
        assert hilbert_index(point, bits=bits) == i
    for a, b in zip(points, points[1:]):
        assert sum(abs(x - y) for x, y in zip(a, b)) == 1


def test_reference_orientation():
    assert [hilbert_coordinates(i, dimensions=2, bits=1) for i in range(4)] == [
        (0, 0),
        (0, 1),
        (1, 1),
        (1, 0),
    ]
    expected = [
        (0, 0),
        (1, 0),
        (1, 1),
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 3),
        (1, 2),
        (2, 2),
        (2, 3),
        (3, 3),
        (3, 2),
        (3, 1),
        (2, 1),
        (2, 0),
        (3, 0),
    ]
    assert [
        hilbert_coordinates(i, dimensions=2, bits=2) for i in range(16)
    ] == expected


@pytest.mark.parametrize(
    "dimensions,bits",
    [(1, 64), (2, 32), (3, 21), (4, 16), (2, 64), (7, 40), (20, 5), (1, 1100)],
)
def test_random_roundtrips_and_native_parity(dimensions, bits):
    rng = random.Random(728)
    for _ in range(40):
        point = tuple(rng.getrandbits(bits) for _ in range(dimensions))
        key = hilbert_index(point, bits=bits)
        assert (
            hilbert_coordinates(key, dimensions=dimensions, bits=bits) == point
        )
        if native_index is not None:
            assert native_index(point, bits=bits) == key
            assert (
                native_coordinates(key, dimensions=dimensions, bits=bits)
                == point
            )


@pytest.mark.parametrize("bits", [0, -1, 1.5, True])
def test_invalid_bits(bits):
    for f in [
        lambda: hilbert_index((0,), bits=bits),
        lambda: hilbert_coordinates(0, dimensions=2, bits=bits),
        lambda: hilbert_order([], bits=bits),
    ]:
        with pytest.raises((ValueError, TypeError)):
            f()


@pytest.mark.parametrize(
    "coordinates", [(), (0, -1), (4, 0), (0.5, 1), (True,)]
)
def test_invalid_coordinates(coordinates):
    with pytest.raises((ValueError, TypeError)):
        hilbert_index(coordinates, bits=2)


@pytest.mark.parametrize(
    "index,dimensions,bits",
    [(-1, 2, 2), (16, 2, 2), (0, 0, 2), (0, 1.5, 2), (True, 2, 2), (1.2, 2, 2)],
)
def test_invalid_decode(index, dimensions, bits):
    with pytest.raises((ValueError, TypeError)):
        hilbert_coordinates(index, dimensions=dimensions, bits=bits)


def test_order_stable_no_mutation_and_inverse():
    points = [(1.0, 1.0), (0.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.9, 0.9)]
    saved = points.copy()
    permutation = hilbert_order(points, bits=1)
    assert points == saved
    assert permutation.index(0) < permutation.index(2) < permutation.index(4)
    ordered = [points[i] for i in permutation]
    restored = [None] * len(points)
    for i, original in enumerate(permutation):
        restored[original] = ordered[i]
    assert restored == saved
    assert hilbert_order([]) == []


def test_quantization_floor_endpoints_constants_and_extremes():
    values = [
        0.0,
        math.nextafter(0.25, 0.0),
        0.25,
        math.nextafter(0.25, 1.0),
        1.0,
    ]
    assert [_quantize((x, 7), ((0.0, 1.0), (7.0, 7.0)), 2) for x in values] == [
        (0, 0),
        (0, 0),
        (1, 0),
        (1, 0),
        (3, 0),
    ]
    assert _quantize((0.0,), ((-1e308, 1e308),), 64) == (1 << 63,)
    assert _quantize((0.5,), ((0.0, 1.0),), 1100) == (1 << 1099,)
    assert _quantize((-5.0, 9.0), ((0.0, 1.0), (3.0, 3.0)), 8, clamp=True) == (
        0,
        0,
    )


@pytest.mark.parametrize(
    "points,bounds",
    [
        ([(float("nan"), 0)], None),
        ([(0, float("inf"))], None),
        ([(0,)], [(0, 1), (0, 1)]),
        ([(0, 0), (0,)], None),
        ([()], None),
        ([(0,)], [(1, 0)]),
        ([(0,)], [(0, float("inf"))]),
        ([(2,)], [(0, 1)]),
        ([(2,)], [(0, 0)]),
        ([(0,)], [(0,)]),
        ([], [(2, 1)]),
    ],
)
def test_invalid_order(points, bounds):
    with pytest.raises((ValueError, TypeError)):
        hilbert_order(points, bounds=bounds)


def test_hilbert_class_basic_2d():
    points = [(0.0, 0.0), (5.0, 5.0), (10.0, 10.0), (1.0, 2.0)]
    h = Hilbert(points=points)

    assert len(h) == 4
    assert h.axis_count == 2
    assert h.dimensions == 2
    order = h.hilbert_order()
    assert order == h.order
    assert set(order) == {0, 1, 2, 3}

    # Exact matches
    for idx, point in enumerate(points):
        assert h.closest_idx(point) == idx
        assert h.closest_point(point) == point
        assert h.closest_hilbert_idx(point) == idx
        assert h.closest_hilbert_point(point) == point

    # Batch queries
    assert h.closest_indices(points) == list(range(len(points)))
    assert h.closest_indices(points=points) == list(range(len(points)))
    assert h.closest_indicies(points) == list(range(len(points)))
    assert h.closest_indicies(points=points) == list(range(len(points)))
    assert h.closest_points(points) == points
    assert h.closest_points(points=points) == points
    assert h.closest_hilbert_indices(points) == list(range(len(points)))
    assert h.closest_hilbert_indicies(points) == list(range(len(points)))
    assert h.closest_hilbert_points(points) == points

    # Proximity queries
    assert h.closest_point((9.0, 9.0)) == (10.0, 10.0)
    assert h.closest_idx((9.0, 9.0)) == 2


def test_hilbert_class_1d():
    points = [(1.0,), (5.0,), (10.0,), (20.0,)]
    h = Hilbert(points)
    assert h.closest_point((6.0,)) == (5.0,)
    assert h.closest_idx((6.0,)) == 1
    assert h.closest_point((18.0,)) == (20.0,)
    assert h.closest_point((0.0,)) == (1.0,)


def test_hilbert_class_3d_and_4d():
    p3 = [(0.0, 0.0, 0.0), (10.0, 10.0, 10.0), (5.0, 5.0, 5.0)]
    h3 = Hilbert(points=p3)
    assert h3.closest_point((9.0, 10.0, 9.0)) == (10.0, 10.0, 10.0)
    assert h3.closest_point((-1.0, 0.0, 1.0)) == (0.0, 0.0, 0.0)

    p4 = [(0.0, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0, 1.0), (5.0, 5.0, 5.0, 5.0)]
    h4 = Hilbert(points=p4)
    assert h4.closest_point((1.1, 0.9, 1.0, 1.0)) == (1.0, 1.0, 1.0, 1.0)


def test_hilbert_class_empty_and_clamping():
    h_empty = Hilbert([])
    assert len(h_empty) == 0
    assert h_empty.hilbert_order() == []
    assert h_empty.closest_points([]) == []
    assert h_empty.closest_indices([]) == []

    with pytest.raises(ValueError):
        h_empty.closest_point((1.0, 2.0))
    with pytest.raises(ValueError):
        h_empty.closest_idx((1.0, 2.0))
    with pytest.raises(ValueError):
        h_empty.closest_points([(1.0, 2.0)])
    with pytest.raises(ValueError):
        h_empty.closest_indices([(1.0, 2.0)])

    h = Hilbert([(0.0, 0.0), (10.0, 10.0)])
    # Clamping outside bounds
    assert h.closest_point((-100.0, -100.0)) == (0.0, 0.0)
    assert h.closest_point((100.0, 100.0)) == (10.0, 10.0)


def test_hilbert_class_validation_errors():
    h = Hilbert([(0.0, 0.0), (1.0, 1.0)])
    with pytest.raises(ValueError):
        h.closest_point((1.0,))
    with pytest.raises(ValueError):
        h.closest_point((1.0, float("nan")))


def test_hilbert_class_duplicate_points_stability():
    points = [(1.0, 1.0), (0.0, 0.0), (1.0, 1.0)]
    h = Hilbert(points)
    # Exact match for (1.0, 1.0) should pick first occurrence (index 0)
    assert h.closest_idx((1.0, 1.0)) == 0
    assert h.closest_point((1.0, 1.0)) == (1.0, 1.0)


def test_geohilbert_class_basic():
    cities = [
        (34.0522, -118.2437),  # Los Angeles
        (40.7128, -74.0060),  # New York
        (37.7749, -122.4194),  # San Francisco
        (51.5074, -0.1278),  # London
        (48.8566, 2.3522),  # Paris
    ]
    gh = GeoHilbert(points=cities)

    assert len(gh) == 5
    assert gh.bits == 21
    order = gh.hilbert_order()
    assert order == gh.order
    assert set(order) == {0, 1, 2, 3, 4}

    # Exact lookups
    for idx, city in enumerate(cities):
        assert gh.closest_idx(city) == idx
        assert gh.closest_point(city) == city
        assert gh.closest_hilbert_idx(city) == idx
        assert gh.closest_hilbert_point(city) == city

    # Batch queries
    assert gh.closest_indices(cities) == list(range(len(cities)))
    assert gh.closest_indices(points=cities) == list(range(len(cities)))
    assert gh.closest_indicies(cities) == list(range(len(cities)))
    assert gh.closest_indicies(points=cities) == list(range(len(cities)))
    assert gh.closest_points(cities) == cities
    assert gh.closest_points(points=cities) == cities
    assert gh.closest_hilbert_indices(cities) == list(range(len(cities)))
    assert gh.closest_hilbert_indicies(cities) == list(range(len(cities)))
    assert gh.closest_hilbert_points(cities) == cities

    # Proximity queries
    assert gh.closest_point((37.7, -122.4)) == (37.7749, -122.4194)
    assert gh.closest_idx((37.7, -122.4)) == 2
    assert gh.closest_point((34.0, -118.0)) == (34.0522, -118.2437)
    assert gh.closest_idx((34.0, -118.0)) == 0


def test_geohilbert_class_poles_and_equator():
    points = [
        (90.0, 0.0),  # North Pole
        (-90.0, 0.0),  # South Pole
        (0.0, 0.0),  # Equator / Prime Meridian
        (0.0, 180.0),  # Equator / Antimeridian
    ]
    gh = GeoHilbert(points)
    assert len(gh) == 4
    for idx, pt in enumerate(points):
        assert gh.closest_point(pt) == pt
        assert gh.closest_idx(pt) == idx

    # Near North pole
    assert gh.closest_point((89.9, 0.0)) == (90.0, 0.0)
    # Near South pole
    assert gh.closest_point((-89.9, 0.0)) == (-90.0, 0.0)


def test_geohilbert_class_empty():
    gh_empty = GeoHilbert([])
    assert len(gh_empty) == 0
    assert gh_empty.hilbert_order() == []
    assert gh_empty.closest_points([]) == []
    assert gh_empty.closest_indices([]) == []

    with pytest.raises(ValueError):
        gh_empty.closest_point((0.0, 0.0))
    with pytest.raises(ValueError):
        gh_empty.closest_idx((0.0, 0.0))
    with pytest.raises(ValueError):
        gh_empty.closest_points([(0.0, 0.0)])
    with pytest.raises(ValueError):
        gh_empty.closest_indices([(0.0, 0.0)])


def test_geohilbert_class_validation_errors():
    gh = GeoHilbert([(0.0, 0.0), (10.0, 10.0)])
    with pytest.raises(ValueError):
        gh.closest_point((1.0,))
    with pytest.raises(ValueError):
        gh.closest_point((1.0, 2.0, 3.0))
    with pytest.raises(ValueError):
        gh.closest_point((1.0, float("nan")))
    with pytest.raises(ValueError):
        gh.closest_point((float("inf"), 1.0))


def test_geohilbert_parity_with_python():
    rng = random.Random(12345)
    points = [
        (rng.uniform(-90.0, 90.0), rng.uniform(-180.0, 180.0))
        for _ in range(50)
    ]
    gh_native = GeoHilbert(points)
    gh_py = PyGeoHilbert(points)

    assert gh_native.hilbert_order() == gh_py.hilbert_order()

    queries = [
        (rng.uniform(-90.0, 90.0), rng.uniform(-180.0, 180.0))
        for _ in range(25)
    ]
    for q in queries:
        assert gh_native.closest_idx(q) == gh_py.closest_idx(q)
        assert gh_native.closest_point(q) == gh_py.closest_point(q)
