def kdtree(points, depth, axis_count):
    """
    Function:

    - Build a KDTree from a list of points.

    Required Arguments:

    - `points`
        - Type: list of tuples
        - What: A list of points to build the KDTree from

    Optional Arguments:

    - `depth`
        - Type: int
        - What: The current depth in the tree (used for axis selection)
    - `axis_count`
        - Type: int
        - What: The number of dimensions in the points (default is 2 for 2D points)

    Returns:

    - The constructed KDTree as a tuple in the format (point, axis, left, right).
    - Where left and right are subtrees.
    """
    if not points:
        return 0
    axis = depth % axis_count
    points.sort(key=lambda p: p[axis])
    median = len(points) // 2
    return (
        points[median],
        axis,
        kdtree(points=points[:median], depth=depth + 1, axis_count=axis_count),
        kdtree(points=points[median + 1 :], depth=depth + 1, axis_count=axis_count),
    )

def squared_distance(p1, p2, axis_count=2):
    """
    Function:

    - Calculate the squared distance between two points.

    Required Arguments:

    - `p1`
        - Type: tuple
        - What: The first point
    - `p2`
        - Type: tuple
        - What: The second point

    Optional Arguments:

    - `axis_count`
        - Type: int
        - What: The number of dimensions in the points
        - Default: 2 (for 2D points)

    Returns:

    - The squared distance between the two points.
    """
    return sum([(p1[i] - p2[i]) ** 2 for i in range(axis_count)])


def closest_point(
    node, point, best=None, axis_count=2, best_dist=float("inf")
):
    """
    Function:

    - Find the closest point in the KDTree to a given point.

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
    - `axis_count`
        - Type: int
        - What: The number of dimensions in the points (default is 2 for 2D points)
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
    median_node_dist = squared_distance(
        point, median_node, axis_count=axis_count
    )
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
    best, best_dist = closest_point(
        close,
        point,
        best,
        axis_count=axis_count,
        best_dist=best_dist,
    )
    # Check the other side if needed
    if diff**2 < best_dist:
        best, best_dist = closest_point(
            away,
            point,
            best,
            axis_count=axis_count,
            best_dist=best_dist,
        )
    return best, best_dist