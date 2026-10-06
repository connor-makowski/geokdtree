from .core import kdtree
from math import cos, sin, pi


# Speed Utils for the 3D GeoKDTree
def __squared_distance_3d__(p1, p2):
    """
    Function:

    - Calculate the squared distance between two 3D points.

    Required Arguments:

    - `p1`
        - Type: tuple
        - What: The first point in 3D space
    - `p2`
        - Type: tuple
        - What: The second point in 3D space

    Returns:

    - The squared distance between the two 3D points.
    """
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    dz = p1[2] - p2[2]
    return dx * dx + dy * dy + dz * dz


def __closest_point_3d__(node, point, best=None, best_dist=float("inf")):
    """
    Function:

    - Find the closest point in a 3d cartesian system using a KDTree.

    Required Arguments:

    - `node`
        - Type: tuple
        - What: The node of the KDTree
    - `point`
        - Type: tuple
        - What: The point to find the closest point to

    Optional Arguments:

    - `best`
        - Type: tuple or None
        - What: The best point found so far (default is None)
    - `best_dist`
        - Type: float
        - What: The best distance found so far (default is infinity)

    Returns:

    - The closest point found in the KDTree to the given point.
    """
    if node == 0:
        return best, best_dist
    # Get the median node and its distance
    median_node = node[0]
    median_node_dist = __squared_distance_3d__(point, median_node)
    # Update the best point and distance if necessary
    if best is None or median_node_dist < best_dist:
        best = median_node
        best_dist = median_node_dist
    # Calculate the difference for node selection given the current axis
    axis = node[1]
    diff = point[axis] - median_node[axis]
    # Choose side to search
    close, away = (node[2], node[3]) if diff < 0 else (node[3], node[2])
    # Search the close side first
    best, best_dist = __closest_point_3d__(close, point, best, best_dist)
    # Check the other side if needed
    if diff**2 < best_dist:
        best, best_dist = __closest_point_3d__(away, point, best, best_dist)
    return best, best_dist


def __closest_point_per_quadrant_3d__(node, query_xyz, query_lat_lon, points):
    """
    Function:

    - Find the closest point in each of the 4 directional quadrants (ne, nw, se, sw)
      using 3D Euclidean distance in unit sphere space.
    """
    bests_idx = [None, None, None, None]
    best_dists = [float("inf"), float("inf"), float("inf"), float("inf")]

    q_lat, q_lon = query_lat_lon
    qx, qy, qz = query_xyz[0], query_xyz[1], query_xyz[2]

    def _search(curr, active_mask):
        if curr == 0 or curr is None or active_mask == 0:
            return

        median_node = curr[0]  # (x, y, z, idx)
        idx = int(median_node[3])
        lat, lon = points[idx]

        mx, my, mz = median_node[0], median_node[1], median_node[2]
        dist = (
            (qx - mx) * (qx - mx)
            + (qy - my) * (qy - my)
            + (qz - mz) * (qz - mz)
        )

        d_lon = lon - q_lon
        if d_lon > 180.0:
            d_lon -= 360.0
        elif d_lon < -180.0:
            d_lon += 360.0

        is_north = lat >= q_lat
        is_south = lat <= q_lat
        is_east = d_lon >= 0.0 or d_lon == -180.0
        is_west = d_lon <= 0.0 or d_lon == 180.0

        if is_north and is_east and (active_mask & 1):
            if dist < best_dists[0]:
                bests_idx[0] = idx
                best_dists[0] = dist

        if is_north and is_west and (active_mask & 2):
            if dist < best_dists[1]:
                bests_idx[1] = idx
                best_dists[1] = dist

        if is_south and is_east and (active_mask & 4):
            if dist < best_dists[2]:
                bests_idx[2] = idx
                best_dists[2] = dist

        if is_south and is_west and (active_mask & 8):
            if dist < best_dists[3]:
                bests_idx[3] = idx
                best_dists[3] = dist

        axis = curr[1]
        q_val = qx if axis == 0 else (qy if axis == 1 else qz)
        diff = q_val - median_node[axis]

        if diff < 0:
            close, away = curr[2], curr[3]
            close_mask = active_mask
            away_mask = active_mask & (1 | 2) if axis == 2 else active_mask
        else:
            close, away = curr[3], curr[2]
            close_mask = active_mask
            away_mask = active_mask & (4 | 8) if axis == 2 else active_mask

        _search(close, close_mask)

        if away_mask:
            diff_sq = diff * diff
            max_away = 0.0
            if (away_mask & 1) and best_dists[0] > max_away:
                max_away = best_dists[0]
            if (away_mask & 2) and best_dists[1] > max_away:
                max_away = best_dists[1]
            if (away_mask & 4) and best_dists[2] > max_away:
                max_away = best_dists[2]
            if (away_mask & 8) and best_dists[3] > max_away:
                max_away = best_dists[3]

            if diff_sq < max_away:
                _search(away, away_mask)

    _search(node, 15)
    return {
        "ne": bests_idx[0],
        "nw": bests_idx[1],
        "se": bests_idx[2],
        "sw": bests_idx[3],
    }


# Special Serializer to convert lat,lon,index to x,y,z,index
def __lat_lon_idx_to_xyz_idx__(
    lat: int | float, lon: int | float, idx: int = 0
):
    """
    Function:

    - Convert latitude and longitude to Cartesian coordinates (x, y, z) and include an index.

    Required Arguments:

    - `lat`
        - Type: int or float
        - What: The latitude in degrees
    - `lon`
        - Type: int or float
        - What: The longitude in degrees

    Optional Arguments:

    - `idx`
        - Type: int
        - What: An index to include with the coordinates (default is 0)
    """
    lat_rad = lat * pi / 180
    lon_rad = lon * pi / 180
    cos_lat = cos(lat_rad)
    x = cos_lat * cos(lon_rad)
    y = cos_lat * sin(lon_rad)
    z = sin(lat_rad)
    return (x, y, z, idx)


class GeoKDTree:
    def __init__(self, points: list[tuple]):
        """
        Function:

        - Build a GeoKDTree from a list of latitude and longitude points or an existing KDTree.

        Required Arguments:

        - `points`
            - Type: list of tuples
            - What: A list of latitude and longitude points to build the GeoKDTree from
            - The points should be in the format [(lat1, lon1), (lat2, lon2), ...].

        """
        # Store the original points
        self.points = points
        # Store the KDTree built from the converted points
        self.tree = kdtree(
            [
                __lat_lon_idx_to_xyz_idx__(point[0], point[1], idx)
                for idx, point in enumerate(points)
            ],
            depth=0,
            axis_count=3,
        )

    def closest_idx(self, point: tuple):
        """
        Function:

        - Find the index of the closest point in the GeoKDTree to a given latitude and longitude point.

        Required Arguments:

        - `point`
            - Type: tuple
            - What: The latitude and longitude point to find the closest point to

        Returns:

        - The index of the closest point found in the GeoKDTree to the given latitude and longitude point.
        """
        best, best_dist = __closest_point_3d__(
            self.tree,
            __lat_lon_idx_to_xyz_idx__(point[0], point[1]),
        )
        return int(best[3])

    def closest_point(self, point: tuple):
        """
        Function:

        - Find the closest latitude and longitude point in the GeoKDTree to a given latitude and longitude point.

        Required Arguments:

        - `point`
            - Type: tuple
            - What: The latitude and longitude point to find the closest point to

        Returns:

        - The closest latitude and longitude point found in the GeoKDTree to the given latitude and longitude point.
        """
        return self.points[self.closest_idx(point)]

    def closest_idx_per_quadrant(self, point: tuple):
        """
        Function:

        - Find the index of the closest point in each quadrant ('ne', 'nw', 'se', 'sw')
          relative to a given (latitude, longitude) point.

        Required Arguments:

        - `point`
            - Type: tuple
            - What: The query point (lat, lon)

        Returns:

        - A dictionary with keys 'ne', 'nw', 'se', 'sw' mapped to the closest index or None.
        """
        query_xyz = __lat_lon_idx_to_xyz_idx__(point[0], point[1])
        return __closest_point_per_quadrant_3d__(
            self.tree, query_xyz, point, self.points
        )

    def closest_point_per_quadrant(self, point: tuple):
        """
        Function:

        - Find the closest (lat, lon) point in each quadrant ('ne', 'nw', 'se', 'sw')
          relative to a given (latitude, longitude) point.

        Required Arguments:

        - `point`
            - Type: tuple
            - What: The query point (lat, lon)

        Returns:

        - A dictionary with keys 'ne', 'nw', 'se', 'sw' mapped to the closest (lat, lon) tuple or None.
        """
        indices = self.closest_idx_per_quadrant(point)
        return {
            d: (self.points[idx] if idx is not None else None)
            for d, idx in indices.items()
        }
