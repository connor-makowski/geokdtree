from operator import itemgetter

_GETTERS = [itemgetter(i) for i in range(16)]


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
    getter = _GETTERS[axis] if axis < 16 else itemgetter(axis)
    points.sort(key=getter)
    median = len(points) // 2
    return (
        points[median],
        axis,
        kdtree(points=points[:median], depth=depth + 1, axis_count=axis_count),
        kdtree(
            points=points[median + 1 :], depth=depth + 1, axis_count=axis_count
        ),
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
    if axis_count == 2:
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return dx * dx + dy * dy
    elif axis_count == 3:
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        dz = p1[2] - p2[2]
        return dx * dx + dy * dy + dz * dz
    return sum((p1[i] - p2[i]) ** 2 for i in range(axis_count))


def closest_point(node, point, best=None, axis_count=2, best_dist=float("inf")):
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


def closest_point_per_quadrant_2d(node, point):
    """
    Function:

    - Find the closest point in each of the 4 quadrants (ne, nw, se, sw)
      for 2D Cartesian points.

    Required Arguments:

    - `node`
        - Type: tuple
        - What: The root node of the KDTree
    - `point`
        - Type: tuple
        - What: The 2D query point (x, y)

    Returns:

    - A dictionary mapping 'ne', 'nw', 'se', 'sw' to their closest point tuple or None.
    """
    bests = [None, None, None, None]
    best_dists = [float("inf"), float("inf"), float("inf"), float("inf")]

    px, py = point[0], point[1]

    def _search(curr, active_mask):
        if curr == 0 or curr is None or active_mask == 0:
            return

        median_node = curr[0]
        mx, my = median_node[0], median_node[1]
        dist = (px - mx) * (px - mx) + (py - my) * (py - my)

        is_east = mx >= px
        is_west = mx <= px
        is_north = my >= py
        is_south = my <= py

        if is_north and is_east and (active_mask & 1):
            if dist < best_dists[0]:
                bests[0] = median_node
                best_dists[0] = dist

        if is_north and is_west and (active_mask & 2):
            if dist < best_dists[1]:
                bests[1] = median_node
                best_dists[1] = dist

        if is_south and is_east and (active_mask & 4):
            if dist < best_dists[2]:
                bests[2] = median_node
                best_dists[2] = dist

        if is_south and is_west and (active_mask & 8):
            if dist < best_dists[3]:
                bests[3] = median_node
                best_dists[3] = dist

        axis = curr[1]
        diff = point[axis] - median_node[axis]

        if diff < 0:
            close, away = curr[2], curr[3]
            close_mask = active_mask
            away_mask = (
                active_mask & (1 | 4) if axis == 0 else active_mask & (1 | 2)
            )
        else:
            close, away = curr[3], curr[2]
            close_mask = active_mask
            away_mask = (
                active_mask & (2 | 8) if axis == 0 else active_mask & (4 | 8)
            )

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
    return {"ne": bests[0], "nw": bests[1], "se": bests[2], "sw": bests[3]}
