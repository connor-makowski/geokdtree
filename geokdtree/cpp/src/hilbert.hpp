#pragma once
// Standalone standard-library Hilbert transform and spatial index.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <limits>
#include <optional>
#include <stdexcept>
#include <utility>
#include <vector>

namespace hilbert_helpers {
inline void validate(int dimensions, int bits) {
    if (dimensions <= 0 || bits <= 0 || bits > 64 || dimensions > 64 / bits)
        throw std::invalid_argument("native Hilbert keys require 1..64 total bits");
}

inline uint64_t index_fast(const uint64_t* in_x, int n, int bits) {
    if (n == 1) return in_x[0];
    uint64_t x[16];
    for (int i = 0; i < n; ++i) x[i] = in_x[i];
    for (uint64_t q = uint64_t(1) << (bits - 1); q > 1; q >>= 1) {
        uint64_t p = q - 1;
        for (int i = 0; i < n; ++i) {
            if (x[i] & q) x[0] ^= p;
            else { auto t = (x[0] ^ x[i]) & p; x[0] ^= t; x[i] ^= t; }
        }
    }
    for (int i = 1; i < n; ++i) x[i] ^= x[i - 1];
    uint64_t t = 0;
    for (uint64_t q = uint64_t(1) << (bits - 1); q > 1; q >>= 1)
        if (x[n - 1] & q) t ^= q - 1;
    for (int i = 0; i < n; ++i) x[i] ^= t;
    uint64_t result = 0;
    for (int b = bits - 1; b >= 0; --b)
        for (int i = 0; i < n; ++i) result = (result << 1) | ((x[i] >> b) & 1);
    return result;
}

inline uint64_t index_3d_fast(uint64_t x0, uint64_t x1, uint64_t x2, int bits) {
    for (uint64_t q = uint64_t(1) << (bits - 1); q > 1; q >>= 1) {
        uint64_t p = q - 1;
        if (x0 & q) x0 ^= p;
        if (x1 & q) x0 ^= p;
        else { auto t = (x0 ^ x1) & p; x0 ^= t; x1 ^= t; }
        if (x2 & q) x0 ^= p;
        else { auto t = (x0 ^ x2) & p; x0 ^= t; x2 ^= t; }
    }
    x1 ^= x0;
    x2 ^= x1;
    uint64_t t = 0;
    for (uint64_t q = uint64_t(1) << (bits - 1); q > 1; q >>= 1)
        if (x2 & q) t ^= q - 1;
    x0 ^= t;
    x1 ^= t;
    x2 ^= t;
    uint64_t result = 0;
    for (int b = bits - 1; b >= 0; --b) {
        result = (result << 3) | (((x0 >> b) & 1) << 2) | (((x1 >> b) & 1) << 1) | ((x2 >> b) & 1);
    }
    return result;
}

inline uint64_t index(std::vector<uint64_t> x, int bits) {
    const int n = static_cast<int>(x.size());
    validate(n, bits);
    for (auto v : x)
        if (bits < 64 && v >= (uint64_t(1) << bits))
            throw std::invalid_argument("coordinate outside integer grid");
    return index_fast(x.data(), n, bits);
}

inline std::vector<uint64_t> coordinates(uint64_t value, int dimensions, int bits) {
    validate(dimensions, bits);
    if (bits * dimensions < 64 && value >= (uint64_t(1) << (bits * dimensions)))
        throw std::invalid_argument("index outside integer grid");
    if (dimensions == 1) return {value};
    std::vector<uint64_t> x(dimensions, 0);
    for (int b = 0; b < bits; ++b)
        for (int i = 0; i < dimensions; ++i)
            x[i] |= ((value >> (b * dimensions + dimensions - 1 - i)) & 1) << b;
    uint64_t t = x.back() >> 1;
    for (int i = dimensions - 1; i > 0; --i) x[i] ^= x[i - 1];
    x[0] ^= t;
    for (int b = 1; b < bits; ++b) {
        uint64_t q = uint64_t(1) << b, p = q - 1;
        for (int i = dimensions - 1; i >= 0; --i) {
            if (x[i] & q) x[0] ^= p;
            else { t = (x[0] ^ x[i]) & p; x[0] ^= t; x[i] ^= t; }
        }
    }
    return x;
}

inline uint64_t quantize_axis(double value, double low, double high, int bits, bool clamp, bool is_query = false) {
    if (!std::isfinite(value)) {
        throw std::invalid_argument(is_query ? "query coordinates must be finite" : "coordinates must be finite");
    }
    if (!clamp && (value < low || value > high)) {
        throw std::invalid_argument("point outside explicit bounds");
    }
    uint64_t cells = uint64_t(1) << bits;
    if (low == high || value <= low) {
        return 0;
    }
    if (value >= high) {
        return cells - 1;
    }
    double fraction = (value - low) / (high - low);
    uint64_t cell = static_cast<uint64_t>(fraction * static_cast<double>(cells));
    if (cell >= cells) {
        cell = cells - 1;
    }
    return cell;
}

inline uint64_t quantize_geo_fast(double value, int bits) noexcept {
    if (value <= -1.0) return 0;
    if (value >= 1.0) return (uint64_t(1) << bits) - 1;
    double fraction = (value + 1.0) * 0.5;
    uint64_t cells = uint64_t(1) << bits;
    uint64_t cell = static_cast<uint64_t>(fraction * static_cast<double>(cells));
    if (cell >= cells) cell = cells - 1;
    return cell;
}

} // namespace hilbert_helpers

class NativeHilbert {
public:
    static constexpr int RADIX_BITS = 12;
    static constexpr size_t BUCKETS = 1 << RADIX_BITS;
    int dimensions = 0;
    int bits = 16;
    int shift_bits = 0;
    std::vector<std::pair<double, double>> bounds;
    std::vector<std::vector<double>> points;
    std::vector<uint64_t> keys;
    std::vector<size_t> order;
    std::vector<uint64_t> sorted_keys;
    std::vector<double> sorted_coords_flat;
    std::vector<int> sorted_indices;
    std::vector<uint32_t> bucket_offsets;

    NativeHilbert() = default;

    NativeHilbert(
        std::vector<std::vector<double>> pts,
        int bits_in = 16,
        const std::optional<std::vector<std::pair<double, double>>>& explicit_bounds = std::nullopt
    ) : bits(bits_in), points(std::move(pts)) {
        if (bits <= 0) {
            throw std::invalid_argument("bits must be positive");
        }
        if (!points.empty()) {
            dimensions = static_cast<int>(points[0].size());
            if (dimensions <= 0) {
                throw std::invalid_argument("points must have at least one dimension");
            }
            for (const auto& p : points) {
                if (static_cast<int>(p.size()) != dimensions) {
                    throw std::invalid_argument("all points must have the same dimension");
                }
                for (double v : p) {
                    if (!std::isfinite(v)) {
                        throw std::invalid_argument("coordinates must be finite");
                    }
                }
            }
        } else if (explicit_bounds.has_value()) {
            dimensions = static_cast<int>(explicit_bounds->size());
        } else {
            dimensions = 0;
        }

        if (dimensions > 0) {
            hilbert_helpers::validate(dimensions, bits);
        }

        if (explicit_bounds.has_value()) {
            if (!points.empty() && static_cast<int>(explicit_bounds->size()) != dimensions) {
                throw std::invalid_argument("bounds must match point dimensions");
            }
            for (const auto& b : *explicit_bounds) {
                if (!std::isfinite(b.first) || !std::isfinite(b.second)) {
                    throw std::invalid_argument("bounds must contain finite (lower, upper) pairs");
                }
                if (b.first > b.second) {
                    throw std::invalid_argument("lower bound exceeds upper bound");
                }
            }
            bounds = *explicit_bounds;
        } else if (!points.empty()) {
            bounds.resize(dimensions);
            for (int d = 0; d < dimensions; ++d) {
                double min_v = points[0][d];
                double max_v = points[0][d];
                for (size_t i = 1; i < points.size(); ++i) {
                    min_v = std::min(min_v, points[i][d]);
                    max_v = std::max(max_v, points[i][d]);
                }
                bounds[d] = {min_v, max_v};
            }
        }

        if (!points.empty()) {
            size_t n = points.size();
            keys.resize(n);
            std::vector<uint64_t> coords(dimensions);
            for (size_t i = 0; i < n; ++i) {
                for (int d = 0; d < dimensions; ++d) {
                    coords[d] = hilbert_helpers::quantize_axis(points[i][d], bounds[d].first, bounds[d].second, bits, false);
                }
                keys[i] = hilbert_helpers::index_fast(coords.data(), dimensions, bits);
            }

            order.resize(n);
            for (size_t i = 0; i < n; ++i) order[i] = i;
            std::stable_sort(order.begin(), order.end(), [this](size_t a, size_t b) {
                return keys[a] < keys[b];
            });

            sorted_keys.resize(n);
            sorted_coords_flat.resize(n * dimensions);
            sorted_indices.resize(n);
            for (size_t i = 0; i < n; ++i) {
                size_t orig_idx = order[i];
                sorted_keys[i] = keys[orig_idx];
                sorted_indices[i] = static_cast<int>(orig_idx);
                for (int d = 0; d < dimensions; ++d) {
                    sorted_coords_flat[i * dimensions + d] = points[orig_idx][d];
                }
            }

            int total_bits = dimensions * bits;
            if (n >= 512 && total_bits >= RADIX_BITS) {
                shift_bits = total_bits - RADIX_BITS;
                bucket_offsets.assign(BUCKETS + 1, 0);
                size_t cur_bucket = 0;
                for (size_t i = 0; i < n; ++i) {
                    size_t b = sorted_keys[i] >> shift_bits;
                    while (cur_bucket <= b) {
                        bucket_offsets[cur_bucket++] = static_cast<uint32_t>(i);
                    }
                }
                while (cur_bucket <= BUCKETS) {
                    bucket_offsets[cur_bucket++] = static_cast<uint32_t>(n);
                }
            }
        }
    }

    size_t size() const noexcept { return points.size(); }

    std::vector<size_t> hilbert_order() const { return order; }

    int closest_idx(const std::vector<double>& query) const {
        if (points.empty()) {
            throw std::invalid_argument("tree is empty");
        }
        if (static_cast<int>(query.size()) != dimensions) {
            throw std::invalid_argument("query dimensions must match tree dimensions");
        }
        for (double v : query) {
            if (!std::isfinite(v)) {
                throw std::invalid_argument("query coordinates must be finite");
            }
        }
        uint64_t q_coords[16];
        for (int d = 0; d < dimensions; ++d) {
            q_coords[d] = hilbert_helpers::quantize_axis(query[d], bounds[d].first, bounds[d].second, bits, true, true);
        }
        uint64_t q_key = hilbert_helpers::index_fast(q_coords, dimensions, bits);

        size_t n = sorted_keys.size();
        size_t range_start = 0;
        size_t range_end = n;
        if (!bucket_offsets.empty()) {
            size_t b = q_key >> shift_bits;
            range_start = bucket_offsets[b];
            range_end = bucket_offsets[b + 1];
        }

        auto it = std::lower_bound(sorted_keys.begin() + range_start, sorted_keys.begin() + range_end, q_key);
        size_t pos = std::distance(sorted_keys.begin(), it);

        size_t positions[16];
        size_t pos_count = 0;
        int left = static_cast<int>(pos) - 1;
        while (left >= 0 && pos_count < 8) {
            positions[pos_count++] = static_cast<size_t>(left);
            if (left == 0 || sorted_keys[left - 1] != sorted_keys[left]) break;
            --left;
        }
        int right = static_cast<int>(pos);
        while (right < static_cast<int>(n) && pos_count < 16) {
            positions[pos_count++] = static_cast<size_t>(right);
            if (right == static_cast<int>(n) - 1 || sorted_keys[right + 1] != sorted_keys[right]) break;
            ++right;
        }

        size_t best_pos = positions[0];
        uint64_t best_h_dist = sorted_keys[best_pos] > q_key ? sorted_keys[best_pos] - q_key : q_key - sorted_keys[best_pos];
        double best_e_dist = 0.0;
        const double* pt0 = &sorted_coords_flat[best_pos * dimensions];
        for (int d = 0; d < dimensions; ++d) {
            double diff = pt0[d] - query[d];
            best_e_dist += diff * diff;
        }
        int best_idx = sorted_indices[best_pos];

        for (size_t p_i = 1; p_i < pos_count; ++p_i) {
            size_t c_pos = positions[p_i];
            uint64_t c_key = sorted_keys[c_pos];
            uint64_t c_h_dist = c_key > q_key ? c_key - q_key : q_key - c_key;
            int c_idx = sorted_indices[c_pos];
            const double* cpt = &sorted_coords_flat[c_pos * dimensions];
            double c_e_dist = 0.0;
            for (int d = 0; d < dimensions; ++d) {
                double diff = cpt[d] - query[d];
                c_e_dist += diff * diff;
            }

            if (c_h_dist < best_h_dist ||
                (c_h_dist == best_h_dist && (c_e_dist < best_e_dist ||
                (c_e_dist == best_e_dist && c_idx < best_idx)))) {
                best_pos = c_pos;
                best_h_dist = c_h_dist;
                best_e_dist = c_e_dist;
                best_idx = c_idx;
            }
        }
        return best_idx;
    }

    std::vector<double> closest_point(const std::vector<double>& query) const {
        return points[closest_idx(query)];
    }
};

struct SortedGeoEntry {
    double x = 0.0;
    double y = 0.0;
    double z = 0.0;
    int idx = 0;
};

class NativeGeoHilbert {
public:
    static constexpr int RADIX_BITS = 12;
    static constexpr size_t BUCKETS = 1 << RADIX_BITS;
    int bits = 21;
    int shift_bits = 0;
    std::vector<std::pair<double, double>> original_points;
    std::vector<SortedGeoEntry> sorted_entries;
    std::vector<size_t> order;
    std::vector<uint64_t> sorted_keys;
    std::vector<uint32_t> bucket_offsets;

    NativeGeoHilbert() = default;

    NativeGeoHilbert(
        std::vector<std::pair<double, double>> pts,
        int bits_in = 21
    ) : bits(bits_in), original_points(std::move(pts)) {
        if (bits <= 0) {
            throw std::invalid_argument("bits must be positive");
        }
        hilbert_helpers::validate(3, bits);

        size_t n = original_points.size();
        std::vector<uint64_t> keys(n);

        constexpr double PI = 3.14159265358979323846;
        constexpr double DEG_TO_RAD = PI / 180.0;

        for (size_t i = 0; i < n; ++i) {
            double lat = original_points[i].first;
            double lon = original_points[i].second;
            if (!std::isfinite(lat) || !std::isfinite(lon)) {
                throw std::invalid_argument("coordinates must be finite");
            }
            double lat_rad = lat * DEG_TO_RAD;
            double lon_rad = lon * DEG_TO_RAD;
            double cos_lat = std::cos(lat_rad);
            double x = cos_lat * std::cos(lon_rad);
            double y = cos_lat * std::sin(lon_rad);
            double z = std::sin(lat_rad);

            uint64_t q0 = hilbert_helpers::quantize_geo_fast(x, bits);
            uint64_t q1 = hilbert_helpers::quantize_geo_fast(y, bits);
            uint64_t q2 = hilbert_helpers::quantize_geo_fast(z, bits);
            keys[i] = hilbert_helpers::index_3d_fast(q0, q1, q2, bits);
        }

        order.resize(n);
        for (size_t i = 0; i < n; ++i) order[i] = i;
        std::stable_sort(order.begin(), order.end(), [&keys](size_t a, size_t b) {
            return keys[a] < keys[b];
        });

        sorted_keys.resize(n);
        sorted_entries.resize(n);
        for (size_t i = 0; i < n; ++i) {
            size_t orig_idx = order[i];
            sorted_keys[i] = keys[orig_idx];
            double lat = original_points[orig_idx].first;
            double lon = original_points[orig_idx].second;
            double lat_rad = lat * DEG_TO_RAD;
            double lon_rad = lon * DEG_TO_RAD;
            double cos_lat = std::cos(lat_rad);
            sorted_entries[i] = {
                cos_lat * std::cos(lon_rad),
                cos_lat * std::sin(lon_rad),
                std::sin(lat_rad),
                static_cast<int>(orig_idx)
            };
        }

        if (n >= 512) {
            shift_bits = 3 * bits - RADIX_BITS;
            bucket_offsets.assign(BUCKETS + 1, 0);
            size_t cur_bucket = 0;
            for (size_t i = 0; i < n; ++i) {
                size_t b = sorted_keys[i] >> shift_bits;
                while (cur_bucket <= b) {
                    bucket_offsets[cur_bucket++] = static_cast<uint32_t>(i);
                }
            }
            while (cur_bucket <= BUCKETS) {
                bucket_offsets[cur_bucket++] = static_cast<uint32_t>(n);
            }
        }
    }

    size_t size() const noexcept { return original_points.size(); }

    std::vector<size_t> hilbert_order() const { return order; }

    int closest_idx(double lat, double lon) const {
        if (original_points.empty()) {
            throw std::invalid_argument("tree is empty");
        }
        if (!std::isfinite(lat) || !std::isfinite(lon)) {
            throw std::invalid_argument("query coordinates must be finite");
        }
        constexpr double PI = 3.14159265358979323846;
        constexpr double DEG_TO_RAD = PI / 180.0;
        double lat_rad = lat * DEG_TO_RAD;
        double lon_rad = lon * DEG_TO_RAD;
        double cos_lat = std::cos(lat_rad);
        double qx = cos_lat * std::cos(lon_rad);
        double qy = cos_lat * std::sin(lon_rad);
        double qz = std::sin(lat_rad);

        uint64_t q0 = hilbert_helpers::quantize_geo_fast(qx, bits);
        uint64_t q1 = hilbert_helpers::quantize_geo_fast(qy, bits);
        uint64_t q2 = hilbert_helpers::quantize_geo_fast(qz, bits);
        uint64_t q_key = hilbert_helpers::index_3d_fast(q0, q1, q2, bits);

        size_t n = sorted_keys.size();
        size_t range_start = 0;
        size_t range_end = n;
        if (!bucket_offsets.empty()) {
            size_t b = q_key >> shift_bits;
            range_start = bucket_offsets[b];
            range_end = bucket_offsets[b + 1];
        }

        auto it = std::lower_bound(sorted_keys.begin() + range_start, sorted_keys.begin() + range_end, q_key);
        size_t pos = std::distance(sorted_keys.begin(), it);

        size_t positions[16];
        size_t pos_count = 0;
        int left = static_cast<int>(pos) - 1;
        while (left >= 0 && pos_count < 8) {
            positions[pos_count++] = static_cast<size_t>(left);
            if (left == 0 || sorted_keys[left - 1] != sorted_keys[left]) break;
            --left;
        }
        int right = static_cast<int>(pos);
        while (right < static_cast<int>(n) && pos_count < 16) {
            positions[pos_count++] = static_cast<size_t>(right);
            if (right == static_cast<int>(n) - 1 || sorted_keys[right + 1] != sorted_keys[right]) break;
            ++right;
        }

        size_t best_pos = positions[0];
        uint64_t best_h_dist = sorted_keys[best_pos] > q_key ? sorted_keys[best_pos] - q_key : q_key - sorted_keys[best_pos];
        const auto& e0 = sorted_entries[best_pos];
        double best_e_dist = (e0.x - qx)*(e0.x - qx) + (e0.y - qy)*(e0.y - qy) + (e0.z - qz)*(e0.z - qz);
        int best_idx = e0.idx;

        for (size_t p_i = 1; p_i < pos_count; ++p_i) {
            size_t c_pos = positions[p_i];
            uint64_t c_key = sorted_keys[c_pos];
            uint64_t c_h_dist = c_key > q_key ? c_key - q_key : q_key - c_key;
            const auto& e = sorted_entries[c_pos];
            double c_e_dist = (e.x - qx)*(e.x - qx) + (e.y - qy)*(e.y - qy) + (e.z - qz)*(e.z - qz);
            int c_idx = e.idx;

            if (c_h_dist < best_h_dist ||
                (c_h_dist == best_h_dist && (c_e_dist < best_e_dist ||
                (c_e_dist == best_e_dist && c_idx < best_idx)))) {
                best_pos = c_pos;
                best_h_dist = c_h_dist;
                best_e_dist = c_e_dist;
                best_idx = c_idx;
            }
        }
        return best_idx;
    }

    std::pair<double, double> closest_point(double lat, double lon) const {
        return original_points[closest_idx(lat, lon)];
    }
};
