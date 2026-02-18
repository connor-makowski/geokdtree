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
    return sum(
        [(p1[0] - p2[0]) ** 2, (p1[1] - p2[1]) ** 2, (p1[2] - p2[2]) ** 2]
    )


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
        return best[3]  # Return the index of the closest point

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
