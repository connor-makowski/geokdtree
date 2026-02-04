from geokdtree import GeoKDTree
import random
import time

print("\n===============\nGeoKDTree SCALE Tests:\n===============")


random.seed(42)  # For reproducibility

for magnitude in [3, 4, 5, 6]:
    num_points = 10**magnitude
    start_time = time.time()
    example_points = [
        (random.uniform(-90, 90), random.uniform(-180, 180))
        for _ in range(num_points)
    ]
    print(
        f"n={num_points} GeoKDTree data created in {round((time.time() - start_time) * 1000, 4)} ms"
    )
    start_time = time.time()
    geo_kd_tree = GeoKDTree(points=example_points)
    print(
        f"n={num_points} GeoKDTree built in {round((time.time() - start_time) * 1000, 4)} ms."
    )

    # Choose a random test point
    test_point = (random.uniform(-90, 90), random.uniform(-180, 180))
    start_time = time.time()
    closest_idx = geo_kd_tree.closest_idx(test_point)
    print(
        f"n={num_points} GeoKDTree found in {round((time.time() - start_time) * 1000, 4)} ms."
    )
