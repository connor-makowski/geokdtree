"""Dependency-free N-dimensional Hilbert keys (Skilling's transpose transform).

The orientation starts (0, 0), (0, 1), (1, 1), (1, 0) on a one-bit
2D grid. Integer transforms are exact and have no machine-word limit.
"""

import bisect
from math import cos, isfinite, pi, sin
from operator import index as integer_index

from .core import validate_points

__all__ = [
    "Hilbert",
    "GeoHilbert",
    "hilbert_index",
    "hilbert_coordinates",
    "hilbert_order",
]


def _positive(value, name):
    """
    Function:

    - Validate and convert a value into a positive integer.

    Required Arguments:

    - `value`
        - Type: int
        - What: Value to validate
    - `name`
        - Type: str
        - What: Name of parameter for error messages

    Returns:

    - The positive integer.
    """
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    value = integer_index(value)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def hilbert_index(coordinates, *, bits):
    """
    Function:

    - Encode an integer grid coordinate into a 1D Hilbert index using Skilling's transform.

    Required Arguments:

    - `coordinates`
        - Type: tuple or list of ints
        - What: Nonempty integer grid coordinates, each axis in [0, 2**bits)

    Required Keyword Arguments:

    - `bits`
        - Type: int
        - What: Number of bits per dimension

    Returns:

    - The integer Hilbert curve index.
    """
    bits = _positive(bits, "bits")
    x = list(coordinates)
    if not x:
        raise ValueError("coordinates must have at least one dimension")
    for i, value in enumerate(x):
        if isinstance(value, bool):
            raise TypeError("coordinates must be integers")
        x[i] = integer_index(value)
        if not 0 <= x[i] < (1 << bits):
            raise ValueError("coordinate outside integer grid")
    n = len(x)
    if n == 1:
        return x[0]
    q = 1 << (bits - 1)
    while q > 1:
        p = q - 1
        for i in range(n):
            if x[i] & q:
                x[0] ^= p
            else:
                t = (x[0] ^ x[i]) & p
                x[0] ^= t
                x[i] ^= t
        q >>= 1
    for i in range(1, n):
        x[i] ^= x[i - 1]
    t = 0
    q = 1 << (bits - 1)
    while q > 1:
        if x[-1] & q:
            t ^= q - 1
        q >>= 1
    x = [value ^ t for value in x]
    result = 0
    for bit in range(bits - 1, -1, -1):
        for value in x:
            result = (result << 1) | ((value >> bit) & 1)
    return result


def hilbert_coordinates(index, *, dimensions, bits):
    """
    Function:

    - Decode a 1D Hilbert integer index to integer grid coordinates.

    Required Arguments:

    - `index`
        - Type: int
        - What: The Hilbert curve integer index

    Required Keyword Arguments:

    - `dimensions`
        - Type: int
        - What: Number of dimensions in the coordinate space
    - `bits`
        - Type: int
        - What: Number of bits per dimension

    Returns:

    - A tuple of integer grid coordinates corresponding to the Hilbert index.
    """
    bits = _positive(bits, "bits")
    dimensions = _positive(dimensions, "dimensions")
    if isinstance(index, bool):
        raise TypeError("index must be an integer")
    index = integer_index(index)
    if not 0 <= index < (1 << (dimensions * bits)):
        raise ValueError("index outside Hilbert grid")
    if dimensions == 1:
        return (index,)
    x = [0] * dimensions
    for bit in range(bits):
        for axis in range(dimensions):
            x[axis] |= (
                (index >> (bit * dimensions + dimensions - 1 - axis)) & 1
            ) << bit
    t = x[-1] >> 1
    for i in range(dimensions - 1, 0, -1):
        x[i] ^= x[i - 1]
    x[0] ^= t
    q = 2
    while q < (1 << bits):
        p = q - 1
        for i in range(dimensions - 1, -1, -1):
            if x[i] & q:
                x[0] ^= p
            else:
                t = (x[0] ^ x[i]) & p
                x[0] ^= t
                x[i] ^= t
        q <<= 1
    return tuple(x)


def _points(points, dimensions=None):
    """
    Function:

    - Validate and normalize an iterable of points into a list of tuples.

    Required Arguments:

    - `points`
        - Type: iterable of iterables
        - What: Collection of coordinates to validate

    Optional Arguments:

    - `dimensions`
        - Type: int or None
        - What: Expected dimension count, or None to infer
        - Default: None

    Returns:

    - A list of tuples containing finite float coordinates.
    """
    result = [tuple(point) for point in points]
    if result and dimensions is None:
        dimensions = len(result[0])
    if result and not dimensions:
        raise ValueError("points must have at least one dimension")
    for point in result:
        if len(point) != dimensions:
            raise ValueError("inconsistent point dimensions")
        if not all(isfinite(value) for value in point):
            raise ValueError("coordinates must be finite")
    return result


def _bounds(points, bounds=None, dimensions=None):
    """
    Function:

    - Compute or validate axis bounds for normalization.

    Required Arguments:

    - `points`
        - Type: list of tuples
        - What: List of normalized points

    Optional Arguments:

    - `bounds`
        - Type: tuple of tuples or None
        - What: Explicit (min, max) bounds per dimension
        - Default: None
    - `dimensions`
        - Type: int or None
        - What: Number of dimensions
        - Default: None

    Returns:

    - A tuple of (min, max) pairs per dimension.
    """
    if dimensions is None:
        dimensions = len(points[0]) if points else None
    if bounds is None:
        if not points:
            return ()
        return tuple(
            (min(p[i] for p in points), max(p[i] for p in points))
            for i in range(dimensions)
        )
    bounds = tuple(tuple(pair) for pair in bounds)
    if dimensions is not None and len(bounds) != dimensions:
        raise ValueError("bounds must match point dimensions")
    for pair in bounds:
        if len(pair) != 2 or not all(isfinite(v) for v in pair):
            raise ValueError("bounds must contain finite (lower, upper) pairs")
        if pair[0] > pair[1]:
            raise ValueError("lower bound exceeds upper bound")
    return bounds


def _quantize(point, bounds, bits, *, clamp=False):
    """
    Function:

    - Quantize a continuous point into discrete integer grid cells using axis bounds.

    Required Arguments:

    - `point`
        - Type: tuple of floats
        - What: Continuous coordinate to quantize
    - `bounds`
        - Type: tuple of tuples
        - What: (min, max) bounds per dimension
    - `bits`
        - Type: int
        - What: Number of bits per axis

    Optional Keyword Arguments:

    - `clamp`
        - Type: bool
        - What: Whether to clamp points outside bounds to edge cells
        - Default: False

    Returns:

    - A tuple of integer grid coordinates in [0, 2**bits).
    """
    if len(point) != len(bounds):
        raise ValueError("query dimensions must match tree dimensions")
    cells = 1 << bits
    result = []
    for value, (low, high) in zip(point, bounds):
        if not isfinite(value):
            raise ValueError("coordinates must be finite")
        if not clamp and not low <= value <= high:
            raise ValueError("point outside explicit bounds")
        if low == high or value <= low:
            result.append(0)
        elif value >= high:
            result.append(cells - 1)
        else:
            # as_integer_ratio also exists on int, without a float conversion.
            vn, vd = value.as_integer_ratio()
            ln, ld = low.as_integer_ratio()
            hn, hd = high.as_integer_ratio()
            numerator = (vn * ld - ln * vd) * hd
            denominator = vd * (hn * ld - ln * hd)
            result.append(min(cells - 1, numerator * cells // denominator))
    return tuple(result)


def _keys(points, bounds, bits, *, clamp=False):
    """
    Function:

    - Compute Hilbert integer keys for a list of continuous points.

    Required Arguments:

    - `points`
        - Type: list of tuples
        - What: List of points to compute keys for
    - `bounds`
        - Type: tuple of tuples
        - What: (min, max) bounds per dimension
    - `bits`
        - Type: int
        - What: Number of bits per axis

    Optional Keyword Arguments:

    - `clamp`
        - Type: bool
        - What: Whether to clamp points outside bounds to edge cells
        - Default: False

    Returns:

    - A list of integer Hilbert keys.
    """
    return [
        hilbert_index(_quantize(p, bounds, bits, clamp=clamp), bits=bits)
        for p in points
    ]


class Hilbert:
    """
    Class:

    - N-dimensional spatial index based on the Hilbert space-filling curve.
    - Accepts Cartesian or geographic coordinate tuples, maps them to discrete
      Hilbert curve integers, and provides nearest-neighbor queries and curve
      orderings.
    """

    def __init__(self, points=(), *, bits=16, bounds=None):
        """
        Function:

        - Build a Hilbert spatial index from a list of N-dimensional Cartesian points.

        Optional Arguments:

        - `points`
            - Type: list of tuples
            - What: List of N-dimensional points to index
            - Default: ()
        - `bits`
            - Type: int
            - What: Number of bits per dimension for quantization
            - Default: 16
        - `bounds`
            - Type: list of tuples or None
            - What: Explicit (min, max) bounds per dimension, or None to infer
            - Default: None

        Returns:

        - A Hilbert spatial index object.
        """
        self.bits = _positive(bits, "bits")
        self.points = _points(points)
        self.dimensions = (
            len(self.points[0])
            if self.points
            else (len(bounds) if bounds else 0)
        )
        self.axis_count = self.dimensions
        self.bounds = _bounds(
            self.points,
            bounds,
            self.dimensions if (self.points or bounds) else None,
        )
        if self.points:
            self.keys = _keys(self.points, self.bounds, self.bits)
            self.order = sorted(
                range(len(self.points)), key=self.keys.__getitem__
            )
            self._sorted_keys = [self.keys[i] for i in self.order]
        else:
            self.keys = []
            self.order = []
            self._sorted_keys = []

    def __len__(self):
        return len(self.points)

    def hilbert_order(self):
        """
        Function:

        - Return a stable permutation of indices in Hilbert curve order.

        Returns:

        - A list of dataset indices representing the points ordered along the Hilbert curve.
        """
        return list(self.order)

    def _validate_point(self, point):
        """
        Function:

        - Validate a query point coordinate against the index dimensions.

        Required Arguments:

        - `point`
            - Type: tuple
            - What: Query coordinate to validate

        Returns:

        - A tuple of finite float coordinates.
        """
        if not self.points:
            raise ValueError("tree is empty")
        p = tuple(point)
        if len(p) != self.dimensions:
            raise ValueError("query dimensions must match tree dimensions")
        if not all(isfinite(v) for v in p):
            raise ValueError("query coordinates must be finite")
        return p

    def _candidate_positions(self, q_key):
        """
        Function:

        - Find candidate position indices around a query Hilbert key.

        Required Arguments:

        - `q_key`
            - Type: int
            - What: The Hilbert key to search around

        Returns:

        - A list of candidate position indices in the sorted keys list.
        """
        n = len(self._sorted_keys)
        pos = bisect.bisect_left(self._sorted_keys, q_key)
        left = []
        i = pos - 1
        while i >= 0:
            left.append(i)
            if i == 0 or self._sorted_keys[i - 1] != self._sorted_keys[i]:
                break
            i -= 1
        right = []
        i = pos
        while i < n:
            right.append(i)
            if i == n - 1 or self._sorted_keys[i + 1] != self._sorted_keys[i]:
                break
            i += 1
        return left + right

    def closest_idx(self, point: tuple):
        """
        Function:

        - Find the index of the closest point in the Hilbert index to a given point.

        Required Arguments:

        - `point`
            - Type: tuple
            - What: The point to find the closest point to

        Returns:

        - The index of the closest point found in the dataset.
        """
        p = self._validate_point(point)
        q_coords = _quantize(p, self.bounds, self.bits, clamp=True)
        q_key = hilbert_index(q_coords, bits=self.bits)
        positions = self._candidate_positions(q_key)

        best_pos = positions[0]
        best_idx = self.order[best_pos]
        cand0 = self.points[best_idx]
        best_h_dist = abs(self._sorted_keys[best_pos] - q_key)
        best_e_dist = sum((a - b) ** 2 for a, b in zip(cand0, p))

        for pos in positions[1:]:
            cand_key = self._sorted_keys[pos]
            h_dist = abs(cand_key - q_key)
            idx = self.order[pos]
            cand = self.points[idx]
            e_dist = sum((a - b) ** 2 for a, b in zip(cand, p))
            if h_dist < best_h_dist or (
                h_dist == best_h_dist
                and (
                    e_dist < best_e_dist
                    or (e_dist == best_e_dist and idx < best_idx)
                )
            ):
                best_pos = pos
                best_h_dist = h_dist
                best_e_dist = e_dist
                best_idx = idx

        return best_idx

    def closest_point(self, point: tuple):
        """
        Function:

        - Find the closest point in the Hilbert index to a given point.

        Required Arguments:

        - `point`
            - Type: tuple
            - What: The point to find the closest point to

        Returns:

        - The closest point found in the dataset.
        """
        return self.points[self.closest_idx(point)]

    def closest_indices(self, points: list[tuple[float | int, float | int]]):
        """
        Function:

        - Return original dataset indices for a list of query points in query order.

        Required Arguments:

        - `points`
            - Type: list[tuple[float | int, float | int]]
            - What: A list of query coordinate tuples

        Returns:

        - A list of original dataset indices matching query order.
        """
        pts = validate_points(points, self.dimensions)
        if pts and not self.points:
            raise ValueError("tree is empty")
        return [self.closest_idx(q) for q in pts]

    closest_indicies = closest_indices

    def closest_points(self, points: list[tuple[float | int, float | int]]):
        """
        Function:

        - Return closest point tuples for a list of query points in query order.

        Required Arguments:

        - `points`
            - Type: list[tuple[float | int, float | int]]
            - What: A list of query coordinate tuples

        Returns:

        - A list of closest point tuples matching query order.
        """
        return [self.points[i] for i in self.closest_indices(points)]

    closest_hilbert_idx = closest_idx
    closest_hilbert_point = closest_point
    closest_hilbert_indices = closest_indices
    closest_hilbert_indicies = closest_indices
    closest_hilbert_points = closest_points


def _lat_lon_to_xyz(lat: float | int, lon: float | int):
    """
    Function:

    - Convert latitude and longitude in degrees to 3D Cartesian coordinates on a unit sphere.

    Required Arguments:

    - `lat`
        - Type: int or float
        - What: Latitude in degrees
    - `lon`
        - Type: int or float
        - What: Longitude in degrees

    Returns:

    - A tuple of (x, y, z) coordinates on the unit sphere.
    """
    lat_rad = lat * pi / 180.0
    lon_rad = lon * pi / 180.0
    cos_lat = cos(lat_rad)
    return (cos_lat * cos(lon_rad), cos_lat * sin(lon_rad), sin(lat_rad))


class GeoHilbert:
    """
    Class:

    - Geographic spatial index based on the 3D Hilbert space-filling curve.
    - Projects (latitude, longitude) coordinates onto the 3D unit sphere
      and provides nearest-neighbor lookups and Hilbert curve ordering.
    """

    def __init__(
        self,
        points: list[tuple[float | int, float | int]] = (),
        *,
        bits: int = 21,
    ):
        """
        Function:

        - Build a GeoHilbert spatial index from a list of latitude and longitude points.

        Optional Arguments:

        - `points`
            - Type: list[tuple[float | int, float | int]]
            - What: A list of (latitude, longitude) pairs
            - Default: ()
        - `bits`
            - Type: int
            - What: Number of bits per dimension for quantization (default 21 for 3D <= 63 bits)
            - Default: 21

        Returns:

        - A GeoHilbert spatial index object.
        """
        self.bits = _positive(bits, "bits")
        self.points = _points(points, dimensions=2)
        xyz_points = [_lat_lon_to_xyz(p[0], p[1]) for p in self.points]
        bounds = ((-1.0, 1.0), (-1.0, 1.0), (-1.0, 1.0))
        self._hilbert = Hilbert(xyz_points, bits=self.bits, bounds=bounds)
        self.order = self._hilbert.order

    def __len__(self):
        return len(self.points)

    def hilbert_order(self):
        """
        Function:

        - Return a stable permutation of indices in Hilbert curve order.

        Returns:

        - A list of dataset indices representing the points ordered along the Hilbert curve.
        """
        return list(self.order)

    def closest_idx(self, point: tuple):
        """
        Function:

        - Find the index of the closest point in the GeoHilbert index to a given (lat, lon) point.

        Required Arguments:

        - `point`
            - Type: tuple
            - What: The (latitude, longitude) point to find the closest point to

        Returns:

        - The index of the closest point found in the dataset.
        """
        if not self.points:
            raise ValueError("tree is empty")
        if len(point) != 2:
            raise ValueError("query dimensions must match tree dimensions")
        if not all(isfinite(v) for v in point):
            raise ValueError("query coordinates must be finite")
        xyz = _lat_lon_to_xyz(point[0], point[1])
        return self._hilbert.closest_idx(xyz)

    def closest_point(self, point: tuple):
        """
        Function:

        - Find the closest (latitude, longitude) point in the GeoHilbert index.

        Required Arguments:

        - `point`
            - Type: tuple
            - What: The (latitude, longitude) point to find the closest point to

        Returns:

        - The closest (latitude, longitude) point found in the dataset.
        """
        return self.points[self.closest_idx(point)]

    def closest_indices(self, points: list[tuple[float | int, float | int]]):
        """
        Function:

        - Return original dataset indices for a list of (lat, lon) query points in query order.

        Required Arguments:

        - `points`
            - Type: list[tuple[float | int, float | int]]
            - What: A list of (latitude, longitude) coordinate tuples to query

        Returns:

        - A list of original dataset indices matching the query points order.
        """
        pts = validate_points(points, 2)
        if pts and not self.points:
            raise ValueError("tree is empty")
        return [self.closest_idx(p) for p in pts]

    closest_indicies = closest_indices

    def closest_points(self, points: list[tuple[float | int, float | int]]):
        """
        Function:

        - Return closest (latitude, longitude) points for a list of query points in query order.

        Required Arguments:

        - `points`
            - Type: list[tuple[float | int, float | int]]
            - What: A list of (latitude, longitude) coordinate tuples to query

        Returns:

        - A list of closest (latitude, longitude) points matching the query points order.
        """
        return [self.points[i] for i in self.closest_indices(points)]

    closest_hilbert_idx = closest_idx
    closest_hilbert_point = closest_point
    closest_hilbert_indices = closest_indices
    closest_hilbert_indicies = closest_indices
    closest_hilbert_points = closest_points


def hilbert_order(points, *, bits=16, bounds=None):
    """
    Function:

    - Return a stable permutation of floating points in Hilbert curve order.

    Required Arguments:

    - `points`
        - Type: list of tuples
        - What: List of N-dimensional Cartesian points to sort

    Optional Arguments:

    - `bits`
        - Type: int
        - What: Number of bits per dimension for quantization
        - Default: 16
    - `bounds`
        - Type: list of tuples or None
        - What: Explicit (min, max) bounds per dimension, or None to infer
        - Default: None

    Returns:

    - A list of dataset indices representing the points in Hilbert order.
    """
    return Hilbert(points=points, bits=bits, bounds=bounds).hilbert_order()
