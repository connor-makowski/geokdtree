def kdflat(points):
    """
    Function:

    - Build a KDTree from a list of points.

    Required Arguments:

    - `points`
        - Type: list of tuples
        - What: A list of points to build the KDTree from

    Optional Arguments:

    - `axis_count`
        - Type: int
        - What: The number of dimensions in the points (default is 2 for 2D points)

    Returns:

    - TBD
    """
    # Log the idx at the end of each point for tracking vs the original list
    points_idx = [(*point, idx) for idx, point in enumerate(points)]
    points_transposed = [list(i) for i in zip(*points)]
    axis_count = len(points_transposed)
    axes = [-1 for _ in points_idx]
    lefts = [-1 for _ in points_idx]
    rights = [-1 for _ in points_idx]
    root_idx = recursive_kd_flat(points_idx, axes, lefts, rights, depth=0, axis_count=axis_count)
    return {
        "points": points_transposed,
        "axes": axes,
        "lefts": lefts,
        "rights": rights,
        "root": root_idx,
        "axis_count": axis_count,
    }


def recursive_kd_flat(points, axes, lefts, rights, depth, axis_count):
    """
    TBD
    """
    if not points:
        return -1
    axis = depth % axis_count
    points.sort(key=lambda p: p[axis])
    median = len(points) // 2
    node = points[median]
    axes[node[-1]] = axis

    left_idx = recursive_kd_flat(points[:median], axes, lefts, rights, depth + 1, axis_count)
    right_idx = recursive_kd_flat(points[median + 1 :], axes, lefts, rights, depth + 1, axis_count)
    lefts[node[-1]] = left_idx
    rights[node[-1]] = right_idx
    return node[-1]

def squared_distance(p1, p2, axis_count=2):
    """
    TBD
    """
    return sum([(p1[i] - p2[i]) ** 2 for i in range(axis_count)])

def closest_point(kdflat_tree, target_point):
    """
    TBD
    """
    idx, distance = recursive_closest_point_flat(
        points=kdflat_tree["points"],
        axes=kdflat_tree["axes"],
        lefts=kdflat_tree["lefts"],
        rights=kdflat_tree["rights"],
        axis_count=kdflat_tree["axis_count"],
        current_idx=kdflat_tree["root"],
        target_point=target_point,
        best=None,
        best_dist=float("inf"),
    )
    return {
        'point_index': idx,
        'point': tuple(kdflat_tree["points"][i][idx] for i in range(kdflat_tree["axis_count"])),
        'distance': distance
    }

def recursive_closest_point_flat(points, axes, lefts, rights, axis_count, current_idx, target_point, best=None, best_dist=float("inf")):
    """
    TBD
    """
    if current_idx == -1:
        return best, best_dist

    # Get the median node and its distance
    median_node_dist = sum((points[target_axis][current_idx] - target_axis_value) ** 2 for target_axis, target_axis_value in enumerate(target_point))

    # Update the best point and distance if necessary
    if best is None or median_node_dist < best_dist:
        best = current_idx
        best_dist = median_node_dist
    # Calculate the difference for node selection given the current axis
    axis = axes[current_idx]
    diff = target_point[axis] - points[axis][current_idx]
    # Choose side to search
    close, away = lefts[current_idx], rights[current_idx]
    if diff < 0:
        close, away = away, close
    # Search the close side first
    best, best_dist = recursive_closest_point_flat(
        points=points, 
        axes=axes, 
        lefts=lefts, 
        rights=rights, 
        axis_count=axis_count, 
        current_idx=close, 
        target_point=target_point, 
        best=best, 
        best_dist=best_dist
    )
    # Check the other side if needed
    if diff**2 < best_dist:
        best, best_dist = recursive_closest_point_flat(
            points=points, 
            axes=axes, 
            lefts=lefts, 
            rights=rights, 
            axis_count=axis_count, 
            current_idx=away, 
            target_point=target_point, 
            best=best, 
            best_dist=best_dist
        )
    return best, best_dist




data = [(1,1), (2,1), (3,1), (4,1), (5,1)]

kdflat_tree = kdflat(data)

print(kdflat_tree)

print(closest_point(kdflat_tree, (3.1, 1.2)))



