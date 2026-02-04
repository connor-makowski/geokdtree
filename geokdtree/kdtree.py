from .core import kdtree, closest_point


class KDTree:
    def __init__(self, points):
        """
        Function:

        - Build a KDTree from a list of n dimensional cartesian points.

        Required Arguments:

        - `points`
            - Type: list of tuples
            - What: A list of n dimensional cartesian points to build the KDTree from

        Returns:

        - A KDTree object that can be used to find the closest point to a given point.
        """
        self.tree = kdtree(points, depth=0, axis_count=len(points[0]))

    def closest_point(self, point):
        """
        Function:

        - Find the closest point in the KDTree to a given point.

        Required Arguments:

        - `point`
            - Type: tuple
            - What: The point to find the closest point to

        Returns:

        - The closest point found in the KDTree to the given point.
        """
        return closest_point(self.tree, point)[0]
