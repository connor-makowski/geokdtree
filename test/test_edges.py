import pytest

from geokdtree.geokdtree import __lat_lon_idx_to_xyz_idx__
from geokdtree.geokdtree import GeoKDTree as PyGeoKDTree
from geokdtree.kdtree import KDTree as PyKDTree

try:
    from geokdtree.cpp import GeoKDTree as CppGeoKDTree
    from geokdtree.cpp import KDTree as CppKDTree
except ImportError:
    CppGeoKDTree = None
    CppKDTree = None

KD_TREES = [PyKDTree]
GEO_TREES = [PyGeoKDTree]
if CppKDTree is not None:
    KD_TREES.append(CppKDTree)
if CppGeoKDTree is not None:
    GEO_TREES.append(CppGeoKDTree)


@pytest.mark.parametrize("TreeClass", KD_TREES)
@pytest.mark.parametrize(
    ("point", "expected"),
    [
        ((0.0, 3.0), {"ne", "nw"}),
        ((0.0, -3.0), {"se", "sw"}),
        ((3.0, 0.0), {"ne", "se"}),
        ((-3.0, 0.0), {"nw", "sw"}),
        ((0.0, 0.0), {"ne", "nw", "se", "sw"}),
    ],
)
def test_cartesian_points_on_quadrant_boundaries(TreeClass, point, expected):
    tree = TreeClass([point])
    result = tree.closest_point_per_quadrant((0.0, 0.0))

    assert {
        key for key, value in result.items() if value is not None
    } == expected
    for quadrant in expected:
        assert result[quadrant] == point


@pytest.mark.parametrize("TreeClass", KD_TREES)
def test_cartesian_quadrants_with_empty_regions(TreeClass):
    points = [(2.0, 2.0), (3.0, 4.0), (-4.0, -2.0)]
    expected_ne = {(2.0, 2.0), (3.0, 4.0)}
    expected_sw = (-4.0, -2.0)
    result = TreeClass(points).closest_point_per_quadrant((0.0, 0.0))

    assert result["ne"] in expected_ne
    assert result["nw"] is None
    assert result["se"] is None
    assert result["sw"] == expected_sw


@pytest.mark.parametrize("TreeClass", KD_TREES)
def test_cartesian_quadrant_ties_return_a_nearest_candidate(TreeClass):
    points = [
        (2.0, 1.0),
        (1.0, 2.0),
        (-2.0, 1.0),
        (-1.0, 2.0),
        (2.0, -1.0),
        (1.0, -2.0),
        (-2.0, -1.0),
        (-1.0, -2.0),
    ]
    expected = {
        "ne": {(2.0, 1.0), (1.0, 2.0)},
        "nw": {(-2.0, 1.0), (-1.0, 2.0)},
        "se": {(2.0, -1.0), (1.0, -2.0)},
        "sw": {(-2.0, -1.0), (-1.0, -2.0)},
    }
    result = TreeClass(points).closest_point_per_quadrant((0.0, 0.0))

    for quadrant, selected in expected.items():
        point = result[quadrant]
        assert point in selected
        assert point[0] ** 2 + point[1] ** 2 == 5.0


@pytest.mark.parametrize("TreeClass", KD_TREES)
def test_cartesian_duplicate_points_and_nearest_tie(TreeClass):
    duplicates = [(1.0, 1.0), (1.0, 1.0)]
    tree = TreeClass(duplicates + [(-1.0, -1.0)])

    assert tree.closest_point((1.0, 1.0)) == duplicates[0]
    assert tree.closest_point((0.0, 0.0)) in {
        (1.0, 1.0),
        (-1.0, -1.0),
    }


@pytest.mark.parametrize("TreeClass", KD_TREES)
def test_cartesian_large_finite_coordinates(TreeClass):
    points = [(1e150, 1e150), (-1e150, -1e150)]
    tree = TreeClass(points)

    assert tree.closest_point((9e149, 9e149)) == (1e150, 1e150)
    assert tree.closest_point((-9e149, -9e149)) == (-1e150, -1e150)


@pytest.mark.parametrize("TreeClass", GEO_TREES)
@pytest.mark.parametrize(
    ("point", "expected"),
    [
        ((0.0, 10.0), {"ne", "se"}),
        ((10.0, 0.0), {"ne", "nw"}),
        ((0.0, 0.0), {"ne", "nw", "se", "sw"}),
    ],
)
def test_geographic_points_on_quadrant_boundaries(TreeClass, point, expected):
    tree = TreeClass([point])
    result = tree.closest_idx_per_quadrant((0.0, 0.0))

    assert {
        key for key, value in result.items() if value is not None
    } == expected
    for quadrant in expected:
        assert result[quadrant] == 0


@pytest.mark.parametrize("TreeClass", GEO_TREES)
def test_geographic_quadrants_with_missing_regions(TreeClass):
    points = [(20.0, 30.0), (10.0, 15.0), (-15.0, -20.0)]
    result = TreeClass(points).closest_idx_per_quadrant((0.0, 0.0))

    assert result["ne"] in {0, 1}
    assert result["nw"] is None
    assert result["se"] is None
    assert result["sw"] == 2


@pytest.mark.parametrize("TreeClass", GEO_TREES)
def test_geographic_antimeridian_and_opposite_longitude(TreeClass):
    points = [
        (10.0, -179.0),
        (10.0, 175.0),
        (-10.0, -179.0),
        (-10.0, 175.0),
    ]
    result = TreeClass(points).closest_idx_per_quadrant((0.0, 179.0))

    assert result == {"ne": 0, "nw": 1, "se": 2, "sw": 3}


@pytest.mark.parametrize("TreeClass", GEO_TREES)
def test_geographic_pole_nearest_and_quadrant_results(TreeClass):
    points = [(90.0, 120.0), (80.0, 0.0), (-90.0, -45.0)]
    tree = TreeClass(points)

    assert tree.closest_idx((89.0, -60.0)) == 0
    result = tree.closest_idx_per_quadrant((90.0, 0.0))
    assert result["ne"] == 0
    assert result["se"] == 0


@pytest.mark.parametrize("TreeClass", GEO_TREES)
def test_geographic_duplicate_points_keep_valid_index(TreeClass):
    points = [(12.5, -45.0), (12.5, -45.0), (-10.0, 120.0)]
    tree = TreeClass(points)

    assert tree.closest_idx(points[0]) in {0, 1}
    assert tree.closest_point(points[0]) == points[0]


@pytest.mark.parametrize("TreeClass", GEO_TREES)
def test_geographic_single_point_has_only_its_quadrant(TreeClass):
    point = (25.0, 40.0)
    result = TreeClass([point]).closest_point_per_quadrant((0.0, 0.0))

    assert result == {"ne": point, "nw": None, "se": None, "sw": None}


@pytest.mark.parametrize("TreeClass", GEO_TREES)
def test_geographic_antipodal_nearest_tie(TreeClass):
    points = [(0.0, 0.0), (0.0, 180.0)]
    closest = TreeClass(points).closest_point((90.0, 0.0))

    assert closest in points


@pytest.mark.parametrize("TreeClass", GEO_TREES)
@pytest.mark.parametrize("count", [1, 15, 16, 17, 31, 32, 33, 64])
def test_geographic_leaf_bucket_sizes_and_quadrants(TreeClass, count):
    signs = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
    points = []
    for i in range(count):
        lat_sign, lon_sign = signs[i % 4]
        scale = 5.0 + i // 4
        points.append((lat_sign * scale, lon_sign * (10.0 + scale)))
    tree = TreeClass(points)
    query = (0.0, 0.0)

    query_xyz = __lat_lon_idx_to_xyz_idx__(*query)[:3]
    distances = []
    for lat, lon in points:
        xyz = __lat_lon_idx_to_xyz_idx__(lat, lon)[:3]
        distances.append(sum((a - b) ** 2 for a, b in zip(query_xyz, xyz)))
    selected_idx = tree.closest_idx(query)
    assert distances[selected_idx] == min(distances)

    expected = {}
    for quadrant, north, east in [
        ("ne", True, True),
        ("nw", True, False),
        ("se", False, True),
        ("sw", False, False),
    ]:
        candidates = [
            i
            for i, (lat, lon) in enumerate(points)
            if (lat >= 0 if north else lat <= 0)
            and (lon >= 0 if east else lon <= 0)
        ]
        expected[quadrant] = (
            min(candidates, key=distances.__getitem__) if candidates else None
        )

    result = tree.closest_idx_per_quadrant(query)
    for quadrant, north, east in [
        ("ne", True, True),
        ("nw", True, False),
        ("se", False, True),
        ("sw", False, False),
    ]:
        idx = expected[quadrant]
        if idx is None:
            assert result[quadrant] is None
        else:
            result_idx = result[quadrant]
            lat, lon = points[result_idx]
            assert (lat >= 0 if north else lat <= 0)
            assert (lon >= 0 if east else lon <= 0)
            assert distances[result_idx] == distances[idx]
