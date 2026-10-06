from .core import kdtree, closest_point, closest_point_per_quadrant_2d


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
        self.axis_count = len(points[0]) if points else 2
        self.tree = kdtree(points, depth=0, axis_count=self.axis_count)

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
        return closest_point(self.tree, point, axis_count=self.axis_count)[0]

    def closest_point_per_quadrant(self, point):
        """
        Function:

        - Find the closest point in each quadrant ('ne', 'nw', 'se', 'sw') for 2D Cartesian points.

        Required Arguments:

        - `point`
            - Type: tuple
            - What: The 2D query point (x, y)

        Returns:

        - A dictionary with keys 'ne', 'nw', 'se', 'sw' mapped to the closest point tuple or None.
        """
        if self.axis_count != 2:
            raise ValueError(
                "closest_point_per_quadrant is only supported for 2D Cartesian points."
            )
        return closest_point_per_quadrant_2d(self.tree, point)
