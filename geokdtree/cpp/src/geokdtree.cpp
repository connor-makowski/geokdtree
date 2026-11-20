#include "geokdtree.hpp"
#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>
#include <string>

namespace kdtree_helpers {
double squared_distance(
    const std::vector<double>& p1,
    const std::vector<double>& p2,
    int axis_count
) {
    double sum = 0.0;
    for (int i = 0; i < axis_count; ++i) {
        double diff = p1[i] - p2[i];
        sum += diff * diff;
    }
    return sum;
}

double squared_distance_3d(
    const std::vector<double>& p1, const std::vector<double>& p2
) {
    double dx = p1[0] - p2[0];
    double dy = p1[1] - p2[1];
    double dz = p1[2] - p2[2];
    return dx * dx + dy * dy + dz * dz;
}

std::vector<double> lat_lon_idx_to_xyz_idx(double lat, double lon, int idx) {
    constexpr double PI = 3.14159265358979323846;
    double lat_rad = lat * PI / 180.0;
    double lon_rad = lon * PI / 180.0;
    double cos_lat = std::cos(lat_rad);
    double x = cos_lat * std::cos(lon_rad);
    double y = cos_lat * std::sin(lon_rad);
    double z = std::sin(lat_rad);
    return {x, y, z, static_cast<double>(idx)};
}

inline double box_dist_sq_2d(
    double px, double py,
    double min_x, double max_x, double min_y, double max_y,
    double cutoff = std::numeric_limits<double>::max()
) {
    double dsq = 0.0;
    if (px < min_x) { double d = min_x - px; dsq += d * d; }
    else if (px > max_x) { double d = px - max_x; dsq += d * d; }
    if (dsq >= cutoff) return dsq;
    if (py < min_y) { double d = min_y - py; dsq += d * d; }
    else if (py > max_y) { double d = py - max_y; dsq += d * d; }
    return dsq;
}

inline double box_dist_sq_3d(
    double qx, double qy, double qz,
    double min_x, double max_x, double min_y, double max_y, double min_z, double max_z,
    double cutoff = std::numeric_limits<double>::max()
) {
    double dsq = box_dist_sq_2d(qx, qy, min_x, max_x, min_y, max_y, cutoff);
    if (dsq >= cutoff) return dsq;
    if (qz < min_z) { double d = min_z - qz; dsq += d * d; }
    else if (qz > max_z) { double d = qz - max_z; dsq += d * d; }
    return dsq;
}

inline double get_max_active_dist(int mask, const double dists[4]) {
    double max_d = 0.0;
    if ((mask & 1) && dists[0] > max_d) max_d = dists[0];
    if ((mask & 2) && dists[1] > max_d) max_d = dists[1];
    if ((mask & 4) && dists[2] > max_d) max_d = dists[2];
    if ((mask & 8) && dists[3] > max_d) max_d = dists[3];
    return max_d;
}

inline void update_quadrant_candidates(
    int node_idx, double dist, int active_mask,
    bool is_north, bool is_south, bool is_east, bool is_west,
    int best_indices[4], double best_dists[4]
) {
    if (is_north && is_east && (active_mask & 1) && dist < best_dists[0]) {
        best_indices[0] = node_idx; best_dists[0] = dist;
    }
    if (is_north && is_west && (active_mask & 2) && dist < best_dists[1]) {
        best_indices[1] = node_idx; best_dists[1] = dist;
    }
    if (is_south && is_east && (active_mask & 4) && dist < best_dists[2]) {
        best_indices[2] = node_idx; best_dists[2] = dist;
    }
    if (is_south && is_west && (active_mask & 8) && dist < best_dists[3]) {
        best_indices[3] = node_idx; best_dists[3] = dist;
    }
}

template <typename T, typename F>
inline std::unordered_map<std::string, std::optional<T>> make_quad_map(
    const int best_indices[4], F&& get_val
) {
    std::unordered_map<std::string, std::optional<T>> res;
    res["ne"] = (best_indices[0] >= 0) ? std::optional<T>(get_val(best_indices[0])) : std::nullopt;
    res["nw"] = (best_indices[1] >= 0) ? std::optional<T>(get_val(best_indices[1])) : std::nullopt;
    res["se"] = (best_indices[2] >= 0) ? std::optional<T>(get_val(best_indices[2])) : std::nullopt;
    res["sw"] = (best_indices[3] >= 0) ? std::optional<T>(get_val(best_indices[3])) : std::nullopt;
    return res;
}
}  // namespace kdtree_helpers

// ============================================================================
// KDTree Implementation
// ============================================================================

KDTree::KDTree(const std::vector<std::vector<double>>& points) {
    if (points.empty()) {
        throw std::invalid_argument("Cannot build KDTree from empty point list");
    }

    dimensions = static_cast<int>(points[0].size());
    if (dimensions == 2) {
        nodes_2d.clear();
        nodes_2d.reserve(points.size());
        std::vector<KDPoint2D> pts(points.size());
        for (size_t i = 0; i < points.size(); ++i) {
            pts[i] = {points[i][0], points[i][1], static_cast<int>(i)};
        }
        root = build_tree_2d(pts, 0, pts.size(), 0);
    } else {
        nodes_nd.clear();
        nodes_nd.reserve(points.size());
        nd_coords.clear();
        nd_coords.reserve(points.size() * dimensions);
        std::vector<std::vector<double>> points_copy = points;
        root = build_tree_nd(points_copy, 0, points_copy.size(), 0, dimensions);
    }
}

KDTree::KDTree(std::vector<std::vector<double>>&& points) {
    if (points.empty()) {
        throw std::invalid_argument("Cannot build KDTree from empty point list");
    }

    dimensions = static_cast<int>(points[0].size());
    if (dimensions == 2) {
        nodes_2d.clear();
        nodes_2d.reserve(points.size());
        std::vector<KDPoint2D> pts(points.size());
        for (size_t i = 0; i < points.size(); ++i) {
            pts[i] = {points[i][0], points[i][1], static_cast<int>(i)};
        }
        root = build_tree_2d(pts, 0, pts.size(), 0);
    } else {
        nodes_nd.clear();
        nodes_nd.reserve(points.size());
        nd_coords.clear();
        nd_coords.reserve(points.size() * dimensions);
        root = build_tree_nd(points, 0, points.size(), 0, dimensions);
    }
}

KDTree::KDTree(std::vector<KDPoint2D> pts) {
    if (pts.empty()) {
        throw std::invalid_argument("Cannot build KDTree from empty point list");
    }
    dimensions = 2;
    nodes_2d.clear();
    nodes_2d.reserve(pts.size());
    root = build_tree_2d(pts, 0, pts.size(), 0);
}

int KDTree::build_tree_2d(
    std::vector<KDPoint2D>& points,
    size_t start,
    size_t end,
    int depth
) {
    if (start >= end) return -1;

    int axis = depth % 2;
    size_t median = start + (end - start) / 2;

    if (axis == 0) {
        std::nth_element(
            points.begin() + start,
            points.begin() + median,
            points.begin() + end,
            [](const KDPoint2D& a, const KDPoint2D& b) {
                return a.x < b.x;
            }
        );
    } else {
        std::nth_element(
            points.begin() + start,
            points.begin() + median,
            points.begin() + end,
            [](const KDPoint2D& a, const KDPoint2D& b) {
                return a.y < b.y;
            }
        );
    }

    int node_idx = static_cast<int>(nodes_2d.size());
    nodes_2d.emplace_back();

    auto& node = nodes_2d[node_idx];
    const auto& pt = points[median];
    node.x = pt.x;
    node.y = pt.y;
    node.idx = pt.idx;
    node.axis = axis;
    node.min_x = node.max_x = pt.x;
    node.min_y = node.max_y = pt.y;

    int left = build_tree_2d(points, start, median, depth + 1);
    int right = build_tree_2d(points, median + 1, end, depth + 1);

    nodes_2d[node_idx].left = left;
    nodes_2d[node_idx].right = right;

    if (left >= 0) {
        node.min_x = std::min(node.min_x, nodes_2d[left].min_x);
        node.max_x = std::max(node.max_x, nodes_2d[left].max_x);
        node.min_y = std::min(node.min_y, nodes_2d[left].min_y);
        node.max_y = std::max(node.max_y, nodes_2d[left].max_y);
    }
    if (right >= 0) {
        node.min_x = std::min(node.min_x, nodes_2d[right].min_x);
        node.max_x = std::max(node.max_x, nodes_2d[right].max_x);
        node.min_y = std::min(node.min_y, nodes_2d[right].min_y);
        node.max_y = std::max(node.max_y, nodes_2d[right].max_y);
    }

    return node_idx;
}

int KDTree::build_tree_nd(
    std::vector<std::vector<double>>& points,
    size_t start,
    size_t end,
    int depth,
    int axis_count
) {
    if (start >= end) return -1;

    int axis = depth % axis_count;
    size_t median = start + (end - start) / 2;

    std::nth_element(
        points.begin() + start,
        points.begin() + median,
        points.begin() + end,
        [axis](const std::vector<double>& a, const std::vector<double>& b) {
            return a[axis] < b[axis];
        }
    );

    int node_idx = static_cast<int>(nodes_nd.size());
    nodes_nd.emplace_back();
    auto& node = nodes_nd[node_idx];
    node.coord_offset = nd_coords.size();
    nd_coords.insert(nd_coords.end(), points[median].begin(), points[median].end());
    node.axis = axis;

    int left = build_tree_nd(points, start, median, depth + 1, axis_count);
    int right = build_tree_nd(points, median + 1, end, depth + 1, axis_count);

    nodes_nd[node_idx].left = left;
    nodes_nd[node_idx].right = right;

    return node_idx;
}

void KDTree::find_closest_2d(
    const KDNode2D* nodes_ptr,
    int node_idx,
    double px,
    double py,
    int& best_node,
    double& best_dist
) const {
    if (node_idx < 0) return;

    const auto& node = nodes_ptr[node_idx];
    if (kdtree_helpers::box_dist_sq_2d(
            px, py, node.min_x, node.max_x, node.min_y, node.max_y, best_dist
        ) >= best_dist) {
        return;
    }

    double dx = px - node.x;
    double dy = py - node.y;
    double node_dist = dx * dx + dy * dy;

    if (node_dist < best_dist) {
        best_node = node_idx;
        best_dist = node_dist;
    }

    int axis = node.axis;
    double diff = (axis == 0 ? dx : dy);
    int close = (diff < 0) ? node.left : node.right;
    int away = (diff < 0) ? node.right : node.left;

    find_closest_2d(nodes_ptr, close, px, py, best_node, best_dist);

    if (diff * diff < best_dist) {
        find_closest_2d(nodes_ptr, away, px, py, best_node, best_dist);
    }
}

std::pair<double, double> KDTree::closest_point_2d(double px, double py) const {
    if (root < 0) throw std::runtime_error("KDTree is empty");
    const KDNode2D* nodes_ptr = nodes_2d.data();
    int best_node = -1;
    double best_dist = std::numeric_limits<double>::max();
    find_closest_2d(nodes_ptr, root, px, py, best_node, best_dist);
    return {nodes_ptr[best_node].x, nodes_ptr[best_node].y};
}

void KDTree::find_closest_nd(
    const KDNodeND* nodes_ptr,
    const double* coords_ptr,
    int node_idx,
    const double* query,
    int& best_node,
    double& best_dist,
    int axis_count
) const {
    if (node_idx < 0) return;

    const auto& node = nodes_ptr[node_idx];
    const double* node_data = coords_ptr + node.coord_offset;
    double node_dist =
        kdtree_helpers::squared_distance_raw(query, node_data, axis_count);

    if (best_node < 0 || node_dist < best_dist) {
        best_node = node_idx;
        best_dist = node_dist;
    }

    int axis = node.axis;
    double diff = query[axis] - node_data[axis];
    int close = (diff < 0) ? node.left : node.right;
    int away = (diff < 0) ? node.right : node.left;

    find_closest_nd(
        nodes_ptr, coords_ptr, close, query, best_node, best_dist, axis_count
    );

    if (diff * diff < best_dist) {
        find_closest_nd(
            nodes_ptr, coords_ptr, away, query, best_node, best_dist, axis_count
        );
    }
}

const double* KDTree::closest_point_data(const double* query) const {
    if (root < 0) throw std::runtime_error("KDTree is empty");
    int best_node = -1;
    double best_dist = std::numeric_limits<double>::max();
    const KDNodeND* nodes_ptr = nodes_nd.data();
    const double* coords_ptr = nd_coords.data();
    find_closest_nd(
        nodes_ptr, coords_ptr, root, query, best_node, best_dist, dimensions
    );
    return coords_ptr + nodes_ptr[best_node].coord_offset;
}

std::vector<double> KDTree::closest_point(const std::vector<double>& point) const {
    if (root < 0) throw std::runtime_error("KDTree is empty");
    if (dimensions == 2) {
        auto res = closest_point_2d(point[0], point[1]);
        return {res.first, res.second};
    }
    const double* data = closest_point_data(point.data());
    return std::vector<double>(data, data + dimensions);
}

void KDTree::closest_points_2d_batch(
    const std::vector<std::pair<double, double>>& queries,
    std::pair<double, double>* out_points
) const {
    if (root < 0) throw std::runtime_error("KDTree is empty");
    const KDNode2D* nodes_ptr = nodes_2d.data();
    const size_t n = queries.size();
    for (size_t i = 0; i < n; ++i) {
        int best_node = -1;
        double best_dist = std::numeric_limits<double>::max();
        find_closest_2d(
            nodes_ptr, root, queries[i].first, queries[i].second, best_node,
            best_dist
        );
        out_points[i] = {nodes_ptr[best_node].x, nodes_ptr[best_node].y};
    }
}

void KDTree::closest_point_per_quadrant_2d_raw(
    double px,
    double py,
    int best_indices[4]
) const {
    if (root < 0) throw std::runtime_error("KDTree is empty");
    best_indices[0] = best_indices[1] = best_indices[2] = best_indices[3] = -1;
    double best_dists[4] = {
        std::numeric_limits<double>::max(),
        std::numeric_limits<double>::max(),
        std::numeric_limits<double>::max(),
        std::numeric_limits<double>::max()
    };
    find_closest_point_per_quadrant_2d(
        nodes_2d.data(), root, px, py, 15, best_indices, best_dists
    );
}

std::unordered_map<std::string, std::optional<std::vector<double>>>
KDTree::closest_point_per_quadrant(const std::vector<double>& point) const {
    if (dimensions != 2) {
        throw std::invalid_argument("closest_point_per_quadrant is only supported for 2D Cartesian points.");
    }
    int best_indices[4];
    closest_point_per_quadrant_2d_raw(point[0], point[1], best_indices);
    return kdtree_helpers::make_quad_map<std::vector<double>>(best_indices, [&](int idx) {
        return std::vector<double>{nodes_2d[idx].x, nodes_2d[idx].y};
    });
}

void KDTree::find_closest_point_per_quadrant_2d(
    const KDNode2D* nodes_ptr,
    int node_idx,
    double px,
    double py,
    int active_mask,
    int best_indices[4],
    double best_dists[4]
) const {
    if (node_idx < 0 || active_mask == 0) return;

    const auto& node = nodes_ptr[node_idx];
    if (node.min_x > px) active_mask &= (1 | 4);
    else if (node.max_x < px) active_mask &= (2 | 8);

    if (node.min_y > py) active_mask &= (1 | 2);
    else if (node.max_y < py) active_mask &= (4 | 8);

    if (active_mask == 0) return;

    double max_active_d = kdtree_helpers::get_max_active_dist(active_mask, best_dists);
    double box_dist_sq = kdtree_helpers::box_dist_sq_2d(
        px, py, node.min_x, node.max_x, node.min_y, node.max_y, max_active_d
    );
    if (box_dist_sq >= max_active_d) return;

    double dx = px - node.x;
    double dy = py - node.y;
    double dist = dx * dx + dy * dy;
    if (dist < max_active_d) {
        kdtree_helpers::update_quadrant_candidates(
            node_idx, dist, active_mask,
            node.y >= py, node.y <= py, node.x >= px, node.x <= px,
            best_indices, best_dists
        );
    }

    int axis = node.axis;
    double diff = (axis == 0 ? px - node.x : py - node.y);
    int close = (diff < 0) ? node.left : node.right;
    int away = (diff < 0) ? node.right : node.left;
    int away_mask = (axis == 0)
        ? (active_mask & (diff < 0 ? (1 | 4) : (2 | 8)))
        : (active_mask & (diff < 0 ? (1 | 2) : (4 | 8)));

    find_closest_point_per_quadrant_2d(nodes_ptr, close, px, py, active_mask, best_indices, best_dists);

    if (away >= 0 && away_mask != 0) {
        if (diff * diff < kdtree_helpers::get_max_active_dist(away_mask, best_dists)) {
            find_closest_point_per_quadrant_2d(nodes_ptr, away, px, py, away_mask, best_indices, best_dists);
        }
    }
}

// ============================================================================
// GeoKDTree Implementation
// ============================================================================

GeoKDTree::GeoKDTree(
    std::vector<GeoPointInternal> pts,
    std::vector<std::pair<double, double>> orig
) : original_points(std::move(orig)) {
    if (pts.empty()) throw std::invalid_argument("Cannot build GeoKDTree from empty point list");
    nodes.clear();
    nodes.reserve(2 * ((pts.size() + LEAF_SIZE - 1) / LEAF_SIZE));
    leaf_points.clear();
    leaf_points.reserve(pts.size());
    root = build_tree(pts, 0, pts.size(), 0);
}

GeoKDTree::GeoKDTree(const std::vector<std::pair<double, double>>& points)
    : original_points(points) {
    if (points.empty()) throw std::invalid_argument("Cannot build GeoKDTree from empty point list");

    constexpr double PI = 3.14159265358979323846;
    constexpr double DEG_TO_RAD = PI / 180.0;
    std::vector<GeoPointInternal> pts(points.size());
    for (size_t i = 0; i < points.size(); ++i) {
        double lat = points[i].first, lon = points[i].second;
        double lat_rad = lat * DEG_TO_RAD, lon_rad = lon * DEG_TO_RAD;
        double cos_lat = std::cos(lat_rad);
        pts[i] = {cos_lat * std::cos(lon_rad), cos_lat * std::sin(lon_rad), std::sin(lat_rad), lat, lon, static_cast<int>(i)};
    }
    nodes.clear();
    nodes.reserve(2 * ((points.size() + LEAF_SIZE - 1) / LEAF_SIZE));
    leaf_points.clear();
    leaf_points.reserve(points.size());
    root = build_tree(pts, 0, pts.size(), 0);
}

GeoKDTree::GeoKDTree(std::vector<std::pair<double, double>>&& points)
    : original_points(std::move(points)) {
    if (original_points.empty()) throw std::invalid_argument("Cannot build GeoKDTree from empty point list");

    constexpr double PI = 3.14159265358979323846;
    constexpr double DEG_TO_RAD = PI / 180.0;
    std::vector<GeoPointInternal> pts(original_points.size());
    for (size_t i = 0; i < original_points.size(); ++i) {
        double lat = original_points[i].first, lon = original_points[i].second;
        double lat_rad = lat * DEG_TO_RAD, lon_rad = lon * DEG_TO_RAD;
        double cos_lat = std::cos(lat_rad);
        pts[i] = {cos_lat * std::cos(lon_rad), cos_lat * std::sin(lon_rad), std::sin(lat_rad), lat, lon, static_cast<int>(i)};
    }
    nodes.clear();
    nodes.reserve(2 * ((original_points.size() + LEAF_SIZE - 1) / LEAF_SIZE));
    leaf_points.clear();
    leaf_points.reserve(original_points.size());
    root = build_tree(pts, 0, pts.size(), 0);
}

int GeoKDTree::build_tree(
    std::vector<GeoPointInternal>& points,
    size_t start,
    size_t end,
    int depth
) {
    if (start >= end) return -1;

    if (end - start <= LEAF_SIZE) {
        int node_idx = static_cast<int>(nodes.size());
        nodes.emplace_back();
        auto& node = nodes[node_idx];
        node.leaf_start = leaf_points.size();
        node.leaf_count = end - start;
        const auto& first = points[start];
        node.min_x = node.max_x = first.x;
        node.min_y = node.max_y = first.y;
        node.min_z = node.max_z = first.z;
        for (size_t i = start; i < end; ++i) {
            const auto& pt = points[i];
            leaf_points.push_back(pt);
            node.min_x = std::min(node.min_x, pt.x);
            node.max_x = std::max(node.max_x, pt.x);
            node.min_y = std::min(node.min_y, pt.y);
            node.max_y = std::max(node.max_y, pt.y);
            node.min_z = std::min(node.min_z, pt.z);
            node.max_z = std::max(node.max_z, pt.z);
        }
        return node_idx;
    }

    int axis = depth % 3;
    size_t median = start + (end - start) / 2;

    if (axis == 0) {
        std::nth_element(
            points.begin() + start,
            points.begin() + median,
            points.begin() + end,
            [](const GeoPointInternal& a, const GeoPointInternal& b) {
                return a.x < b.x;
            }
        );
    } else if (axis == 1) {
        std::nth_element(
            points.begin() + start,
            points.begin() + median,
            points.begin() + end,
            [](const GeoPointInternal& a, const GeoPointInternal& b) {
                return a.y < b.y;
            }
        );
    } else {
        std::nth_element(
            points.begin() + start,
            points.begin() + median,
            points.begin() + end,
            [](const GeoPointInternal& a, const GeoPointInternal& b) {
                return a.z < b.z;
            }
        );
    }

    int node_idx = static_cast<int>(nodes.size());
    nodes.emplace_back();

    const auto& pt = points[median];
    nodes[node_idx].x = pt.x; nodes[node_idx].y = pt.y; nodes[node_idx].z = pt.z;
    nodes[node_idx].lat = pt.lat; nodes[node_idx].lon = pt.lon; nodes[node_idx].idx = pt.idx;
    nodes[node_idx].axis = axis;
    nodes[node_idx].min_x = nodes[node_idx].max_x = pt.x;
    nodes[node_idx].min_y = nodes[node_idx].max_y = pt.y;
    nodes[node_idx].min_z = nodes[node_idx].max_z = pt.z;

    int left = build_tree(points, start, median, depth + 1);
    int right = build_tree(points, median + 1, end, depth + 1);

    nodes[node_idx].left = left;
    nodes[node_idx].right = right;

    if (left >= 0) {
        nodes[node_idx].min_x = std::min(nodes[node_idx].min_x, nodes[left].min_x);
        nodes[node_idx].max_x = std::max(nodes[node_idx].max_x, nodes[left].max_x);
        nodes[node_idx].min_y = std::min(nodes[node_idx].min_y, nodes[left].min_y);
        nodes[node_idx].max_y = std::max(nodes[node_idx].max_y, nodes[left].max_y);
        nodes[node_idx].min_z = std::min(nodes[node_idx].min_z, nodes[left].min_z);
        nodes[node_idx].max_z = std::max(nodes[node_idx].max_z, nodes[left].max_z);
    }
    if (right >= 0) {
        nodes[node_idx].min_x = std::min(nodes[node_idx].min_x, nodes[right].min_x);
        nodes[node_idx].max_x = std::max(nodes[node_idx].max_x, nodes[right].max_x);
        nodes[node_idx].min_y = std::min(nodes[node_idx].min_y, nodes[right].min_y);
        nodes[node_idx].max_y = std::max(nodes[node_idx].max_y, nodes[right].max_y);
        nodes[node_idx].min_z = std::min(nodes[node_idx].min_z, nodes[right].min_z);
        nodes[node_idx].max_z = std::max(nodes[node_idx].max_z, nodes[right].max_z);
    }

    return node_idx;
}

void GeoKDTree::find_closest_3d(
    const GeoKDNode* nodes_ptr,
    const GeoPointInternal* leaf_ptr,
    int node_idx,
    double qx,
    double qy,
    double qz,
    int& best_idx,
    double& best_dist
) const {
    if (node_idx < 0) return;

    const auto& node = nodes_ptr[node_idx];
    if (kdtree_helpers::box_dist_sq_3d(
            qx, qy, qz, node.min_x, node.max_x, node.min_y, node.max_y,
            node.min_z, node.max_z, best_dist
        ) >= best_dist) {
        return;
    }

    if (node.leaf_count != 0) {
        const GeoPointInternal* pt = leaf_ptr + node.leaf_start;
        const GeoPointInternal* const end = pt + node.leaf_count;
        double local_best_dist = best_dist;
        int local_best_idx = best_idx;
        for (; pt != end; ++pt) {
            double dx = qx - pt->x;
            double dy = qy - pt->y;
            double dz = qz - pt->z;
            double dist = dx * dx + dy * dy + dz * dz;
            if (dist < local_best_dist) {
                local_best_idx = pt->idx;
                local_best_dist = dist;
            }
        }
        best_dist = local_best_dist;
        best_idx = local_best_idx;
        return;
    }

    double dx = qx - node.x, dy = qy - node.y, dz = qz - node.z;
    double node_dist = dx * dx + dy * dy + dz * dz;

    if (node_dist < best_dist) {
        best_idx = node.idx;
        best_dist = node_dist;
    }

    int axis = node.axis;
    double diff = (axis == 0) ? dx : ((axis == 1) ? dy : dz);
    int close = (diff < 0) ? node.left : node.right;
    int away = (diff < 0) ? node.right : node.left;

    find_closest_3d(nodes_ptr, leaf_ptr, close, qx, qy, qz, best_idx, best_dist);

    if (diff * diff < best_dist) {
        find_closest_3d(nodes_ptr, leaf_ptr, away, qx, qy, qz, best_idx, best_dist);
    }
}

int GeoKDTree::closest_idx(double lat, double lon) const {
    if (root < 0) throw std::runtime_error("GeoKDTree is empty");
    constexpr double PI = 3.14159265358979323846;
    double lat_rad = lat * PI / 180.0, lon_rad = lon * PI / 180.0;
    double cos_lat = std::cos(lat_rad);
    int best_idx = -1;
    double best_dist = std::numeric_limits<double>::max();
    const GeoKDNode* nodes_ptr = nodes.data();
    const GeoPointInternal* leaf_ptr = leaf_points.data();
    find_closest_3d(
        nodes_ptr, leaf_ptr, root, cos_lat * std::cos(lon_rad),
        cos_lat * std::sin(lon_rad), std::sin(lat_rad), best_idx, best_dist
    );
    return best_idx;
}

std::pair<double, double> GeoKDTree::closest_point(double lat, double lon) const {
    return original_points[closest_idx(lat, lon)];
}

namespace {
struct QueryXYZ {
    double x;
    double y;
    double z;
};
constexpr size_t BATCH_CHUNK_SIZE = 1024;
} // namespace

void GeoKDTree::closest_indices_batch(
    const std::vector<std::pair<double, double>>& queries,
    int* out_indices
) const {
    if (root < 0) throw std::runtime_error("GeoKDTree is empty");
    constexpr double PI = 3.14159265358979323846;
    constexpr double DEG_TO_RAD = PI / 180.0;
    const size_t n = queries.size();
    const GeoKDNode* nodes_ptr = nodes.data();
    const GeoPointInternal* leaf_ptr = leaf_points.data();
    QueryXYZ query_xyz[BATCH_CHUNK_SIZE];

    for (size_t chunk_start = 0; chunk_start < n; chunk_start += BATCH_CHUNK_SIZE) {
        const size_t chunk_end = std::min(chunk_start + BATCH_CHUNK_SIZE, n);
        const size_t chunk_len = chunk_end - chunk_start;

        for (size_t j = 0; j < chunk_len; ++j) {
            const auto& q = queries[chunk_start + j];
            double lat_rad = q.first * DEG_TO_RAD;
            double lon_rad = q.second * DEG_TO_RAD;
            double cos_lat = std::cos(lat_rad);
            query_xyz[j] = {
                cos_lat * std::cos(lon_rad),
                cos_lat * std::sin(lon_rad),
                std::sin(lat_rad)
            };
        }

        for (size_t j = 0; j < chunk_len; ++j) {
            int best_idx = -1;
            double best_dist = std::numeric_limits<double>::max();
            find_closest_3d(
                nodes_ptr,
                leaf_ptr,
                root,
                query_xyz[j].x,
                query_xyz[j].y,
                query_xyz[j].z,
                best_idx,
                best_dist
            );
            out_indices[chunk_start + j] = best_idx;
        }
    }
}

void GeoKDTree::closest_points_batch(
    const std::vector<std::pair<double, double>>& queries,
    std::pair<double, double>* out_points
) const {
    if (root < 0) throw std::runtime_error("GeoKDTree is empty");
    constexpr double PI = 3.14159265358979323846;
    constexpr double DEG_TO_RAD = PI / 180.0;
    const size_t n = queries.size();
    const GeoKDNode* nodes_ptr = nodes.data();
    const GeoPointInternal* leaf_ptr = leaf_points.data();
    QueryXYZ query_xyz[BATCH_CHUNK_SIZE];

    for (size_t chunk_start = 0; chunk_start < n; chunk_start += BATCH_CHUNK_SIZE) {
        const size_t chunk_end = std::min(chunk_start + BATCH_CHUNK_SIZE, n);
        const size_t chunk_len = chunk_end - chunk_start;

        for (size_t j = 0; j < chunk_len; ++j) {
            const auto& q = queries[chunk_start + j];
            double lat_rad = q.first * DEG_TO_RAD;
            double lon_rad = q.second * DEG_TO_RAD;
            double cos_lat = std::cos(lat_rad);
            query_xyz[j] = {
                cos_lat * std::cos(lon_rad),
                cos_lat * std::sin(lon_rad),
                std::sin(lat_rad)
            };
        }

        for (size_t j = 0; j < chunk_len; ++j) {
            int best_idx = -1;
            double best_dist = std::numeric_limits<double>::max();
            find_closest_3d(
                nodes_ptr,
                leaf_ptr,
                root,
                query_xyz[j].x,
                query_xyz[j].y,
                query_xyz[j].z,
                best_idx,
                best_dist
            );
            out_points[chunk_start + j] = original_points[best_idx];
        }
    }
}

int GeoKDTree::closest_idx(const std::pair<double, double>& point) const {
    return closest_idx(point.first, point.second);
}

std::pair<double, double> GeoKDTree::closest_point(const std::pair<double, double>& point) const {
    return closest_point(point.first, point.second);
}

void GeoKDTree::closest_idx_per_quadrant_raw(
    double lat,
    double lon,
    int best_indices[4]
) const {
    if (root < 0) throw std::runtime_error("GeoKDTree is empty");
    constexpr double PI = 3.14159265358979323846;
    double lat_rad = lat * PI / 180.0, lon_rad = lon * PI / 180.0;
    double cos_lat = std::cos(lat_rad);
    best_indices[0] = best_indices[1] = best_indices[2] = best_indices[3] = -1;
    double best_dists[4] = {
        std::numeric_limits<double>::max(),
        std::numeric_limits<double>::max(),
        std::numeric_limits<double>::max(),
        std::numeric_limits<double>::max()
    };
    const GeoKDNode* nodes_ptr = nodes.data();
    const GeoPointInternal* leaf_ptr = leaf_points.data();
    find_closest_point_per_quadrant_3d(
        nodes_ptr, leaf_ptr, root,
        cos_lat * std::cos(lon_rad), cos_lat * std::sin(lon_rad), std::sin(lat_rad),
        lat, lon, 15, best_indices, best_dists
    );
}

void GeoKDTree::find_closest_point_per_quadrant_3d(
    const GeoKDNode* nodes_ptr,
    const GeoPointInternal* leaf_ptr,
    int node_idx,
    double qx,
    double qy,
    double qz,
    double q_lat,
    double q_lon,
    int active_mask,
    int best_indices[4],
    double best_dists[4]
) const {
    if (node_idx < 0 || active_mask == 0) return;

    const auto& node = nodes_ptr[node_idx];
    if (node.min_z > qz) active_mask &= (1 | 2);
    else if (node.max_z < qz) active_mask &= (4 | 8);

    if (active_mask == 0) return;

    double max_active_d = kdtree_helpers::get_max_active_dist(active_mask, best_dists);
    double box_dist_sq = kdtree_helpers::box_dist_sq_3d(
        qx, qy, qz,
        node.min_x, node.max_x,
        node.min_y, node.max_y,
        node.min_z, node.max_z,
        max_active_d
    );
    if (box_dist_sq >= max_active_d) return;

    if (node.leaf_count != 0) {
        const GeoPointInternal* pt = leaf_ptr + node.leaf_start;
        const GeoPointInternal* const end = pt + node.leaf_count;
        for (; pt != end; ++pt) {
            double dx = qx - pt->x;
            double dy = qy - pt->y;
            double dz = qz - pt->z;
            double dist = dx * dx + dy * dy + dz * dz;
            if (dist >= max_active_d) continue;

            double d_lon = pt->lon - q_lon;
            if (d_lon > 180.0) d_lon -= 360.0;
            else if (d_lon < -180.0) d_lon += 360.0;
            kdtree_helpers::update_quadrant_candidates(
                pt->idx, dist, active_mask,
                pt->lat >= q_lat, pt->lat <= q_lat,
                (d_lon >= 0.0 || d_lon == -180.0),
                (d_lon <= 0.0 || d_lon == 180.0),
                best_indices, best_dists
            );
            max_active_d = kdtree_helpers::get_max_active_dist(active_mask, best_dists);
        }
        return;
    }

    double dx = qx - node.x, dy = qy - node.y, dz = qz - node.z;
    double dist = dx * dx + dy * dy + dz * dz;
    if (dist < max_active_d) {
        double d_lon = node.lon - q_lon;
        if (d_lon > 180.0) d_lon -= 360.0;
        else if (d_lon < -180.0) d_lon += 360.0;
        kdtree_helpers::update_quadrant_candidates(
            node.idx, dist, active_mask,
            node.lat >= q_lat, node.lat <= q_lat,
            (d_lon >= 0.0 || d_lon == -180.0), (d_lon <= 0.0 || d_lon == 180.0),
            best_indices, best_dists
        );
        max_active_d = kdtree_helpers::get_max_active_dist(active_mask, best_dists);
    }

    int axis = node.axis;
    double q_val = (axis == 0) ? qx : ((axis == 1) ? qy : qz);
    double n_val = (axis == 0) ? node.x : ((axis == 1) ? node.y : node.z);
    double diff = q_val - n_val;
    int close = (diff < 0) ? node.left : node.right;
    int away = (diff < 0) ? node.right : node.left;
    int away_mask = (axis == 2) ? (active_mask & (diff < 0 ? (1 | 2) : (4 | 8))) : active_mask;

    find_closest_point_per_quadrant_3d(
        nodes_ptr, leaf_ptr, close, qx, qy, qz, q_lat, q_lon, active_mask, best_indices, best_dists
    );

    if (away >= 0 && away_mask != 0) {
        if (diff * diff < kdtree_helpers::get_max_active_dist(away_mask, best_dists)) {
            find_closest_point_per_quadrant_3d(
                nodes_ptr, leaf_ptr, away, qx, qy, qz, q_lat, q_lon, away_mask, best_indices, best_dists
            );
        }
    }
}

std::unordered_map<std::string, std::optional<int>>
GeoKDTree::closest_idx_per_quadrant(const std::pair<double, double>& point) const {
    int best_indices[4];
    closest_idx_per_quadrant_raw(point.first, point.second, best_indices);
    return kdtree_helpers::make_quad_map<int>(best_indices, [](int idx) { return idx; });
}

std::unordered_map<std::string, std::optional<std::pair<double, double>>>
GeoKDTree::closest_point_per_quadrant(const std::pair<double, double>& point) const {
    int best_indices[4];
    closest_idx_per_quadrant_raw(point.first, point.second, best_indices);
    return kdtree_helpers::make_quad_map<std::pair<double, double>>(best_indices, [&](int idx) {
        return original_points[idx];
    });
}

std::vector<double> GeoKDTree::lat_lon_idx_to_xyz_idx(
    double lat, double lon, int idx
) {
    return kdtree_helpers::lat_lon_idx_to_xyz_idx(lat, lon, idx);
}
