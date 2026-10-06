#pragma once
#include <algorithm>
#include <cmath>
#include <limits>
#include <memory>
#include <optional>
#include <string>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>

// Result structures
struct ClosestPointResult {
    std::vector<double> point;
    double distance;
};

struct ClosestIdxResult {
    int idx;
    double distance;
};

// Internal 2D point for fast Cartesian building
struct KDPoint2D {
    double x = 0.0;
    double y = 0.0;
    int idx = 0;
};

// 2D KD-Tree node structure (flat arena, inline AABB & coordinates)
struct KDNode2D {
    double x = 0.0;
    double y = 0.0;
    int idx = 0;
    int axis = 0;
    double min_x = 0.0, max_x = 0.0;
    double min_y = 0.0, max_y = 0.0;
    int left = -1;
    int right = -1;

    KDNode2D() = default;
};

// General N-D KD-Tree node structure
struct KDNodeND {
    std::vector<double> point;
    int axis = 0;
    int left = -1;
    int right = -1;

    KDNodeND() = default;
};

// Internal point for GeoKDTree building
struct GeoPointInternal {
    double x = 0.0;
    double y = 0.0;
    double z = 0.0;
    double lat = 0.0;
    double lon = 0.0;
    int idx = 0;
};

// Geo KD-Tree node structure (flat arena, inline AABB, lat/lon & coordinates)
struct GeoKDNode {
    double x = 0.0;
    double y = 0.0;
    double z = 0.0;
    double lat = 0.0;
    double lon = 0.0;
    int idx = 0;
    int axis = 0;
    double min_x = 0.0, max_x = 0.0;
    double min_y = 0.0, max_y = 0.0;
    double min_z = 0.0, max_z = 0.0;
    int left = -1;
    int right = -1;

    GeoKDNode() = default;
};

// Helper functions
namespace kdtree_helpers {
double squared_distance(
    const std::vector<double>& p1,
    const std::vector<double>& p2,
    int axis_count = 2
);
double squared_distance_3d(
    const std::vector<double>& p1, const std::vector<double>& p2
);
std::vector<double> lat_lon_idx_to_xyz_idx(double lat, double lon, int idx = 0);
}  // namespace kdtree_helpers

// Standard KD-Tree class
class KDTree {
private:
    std::vector<KDNode2D> nodes_2d;
    std::vector<KDNodeND> nodes_nd;
    int root = -1;
    int dimensions = 0;

    // 2D specialized build
    int build_tree_2d(
        std::vector<KDPoint2D>& points,
        size_t start,
        size_t end,
        int depth
    );

    // General N-D build
    int build_tree_nd(
        std::vector<std::vector<double>>& points,
        size_t start,
        size_t end,
        int depth,
        int axis_count
    );

    // 2D specialized closest
    void find_closest_2d(
        int node_idx,
        double px,
        double py,
        int& best_node,
        double& best_dist
    ) const;

    // General N-D closest
    void find_closest_nd(
        int node_idx,
        const std::vector<double>& point,
        std::vector<double>& best,
        double& best_dist,
        int axis_count
    ) const;

    // Find closest point per quadrant recursively (2D only)
    void find_closest_point_per_quadrant_2d(
        int node_idx,
        double px,
        double py,
        int active_mask,
        int best_indices[4],
        double best_dists[4]
    ) const;

public:
    // Constructors
    explicit KDTree(const std::vector<std::vector<double>>& points);
    explicit KDTree(std::vector<KDPoint2D> pts);

    int get_dimensions() const { return dimensions; }
    const KDNode2D& get_node_2d(int idx) const { return nodes_2d[idx]; }

    // Fast 2D queries
    std::pair<double, double> closest_point_2d(double px, double py) const;
    void closest_point_per_quadrant_2d_raw(
        double px, double py, int best_indices[4]
    ) const;

    // Standard API methods
    std::vector<double> closest_point(const std::vector<double>& point) const;
    std::unordered_map<std::string, std::optional<std::vector<double>>>
    closest_point_per_quadrant(const std::vector<double>& point) const;
};

// Geographic KD-Tree class (for lat/lon coordinates)
class GeoKDTree {
private:
    std::vector<GeoKDNode> nodes;
    int root = -1;
    std::vector<std::pair<double, double>> original_points;

    // Build tree recursively in-place
    int build_tree(
        std::vector<GeoPointInternal>& points,
        size_t start,
        size_t end,
        int depth
    );

    // Find closest point 3D
    void find_closest_3d(
        int node_idx,
        double qx,
        double qy,
        double qz,
        int& best_idx,
        double& best_dist
    ) const;

    // Find closest point per quadrant recursively
    void find_closest_point_per_quadrant_3d(
        int node_idx,
        double qx,
        double qy,
        double qz,
        double q_lat,
        double q_lon,
        int active_mask,
        int best_indices[4],
        double best_dists[4]
    ) const;

public:
    // Constructors - takes lat/lon pairs
    explicit GeoKDTree(const std::vector<std::pair<double, double>>& points);
    explicit GeoKDTree(std::vector<std::pair<double, double>>&& points);
    GeoKDTree(
        std::vector<GeoPointInternal> pts,
        std::vector<std::pair<double, double>> orig
    );

    const std::pair<double, double>& get_original_point(int idx) const {
        return original_points[idx];
    }

    // Fast direct queries
    int closest_idx(double lat, double lon) const;
    std::pair<double, double> closest_point(double lat, double lon) const;
    void closest_idx_per_quadrant_raw(
        double lat, double lon, int best_indices[4]
    ) const;

    // Standard API methods
    int closest_idx(const std::pair<double, double>& point) const;
    std::pair<double, double> closest_point(
        const std::pair<double, double>& point
    ) const;
    std::unordered_map<std::string, std::optional<int>>
    closest_idx_per_quadrant(const std::pair<double, double>& point) const;
    std::unordered_map<std::string, std::optional<std::pair<double, double>>>
    closest_point_per_quadrant(const std::pair<double, double>& point) const;

    // Static helper for coordinate conversion
    static std::vector<double> lat_lon_idx_to_xyz_idx(
        double lat, double lon, int idx = 0
    );
};