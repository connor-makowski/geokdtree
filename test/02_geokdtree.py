from geokdtree import GeoKDTree

print("\n===============\nBasic GeoKDTree Tests:\n===============")

example_points = [
    (34.0522, -118.2437),  # Los Angeles
    (40.7128, -74.0060),  # New York
    (37.7749, -122.4194),  # San Francisco
    (51.5074, -0.1278),  # London
    (48.8566, 2.3522),  # Paris
]

geo_kd_tree = GeoKDTree(points=example_points)
test_point = (47.6062, -122.3321)  # Seattle

closest_idx = geo_kd_tree.closest_idx(
    test_point
)  # Expect San Francisco to be closest
print(f"Closest point to {test_point} is {example_points[closest_idx] }")
