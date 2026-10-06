#include <nanobind/nanobind.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/pair.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/optional.h>
#include <nanobind/stl/unordered_map.h>
#include <string>
#include <utility>
#include "../src/geokdtree.hpp"

namespace nb = nanobind;

namespace {
inline bool extract_double(PyObject* obj, double& out) noexcept {
    if (__builtin_expect(PyFloat_CheckExact(obj), 1)) {
        out = PyFloat_AS_DOUBLE(obj);
        return true;
    }
    if (PyLong_CheckExact(obj)) {
        out = PyLong_AsDouble(obj);
        return true;
    }
    if (PyFloat_Check(obj)) {
        out = PyFloat_AS_DOUBLE(obj);
        return true;
    }
    if (PyLong_Check(obj)) {
        out = PyLong_AsDouble(obj);
        return true;
    }
    return false;
}

inline std::pair<double, double> parse_point2d(nb::handle h) {
    PyObject* obj = h.ptr();
    if (__builtin_expect(PyTuple_CheckExact(obj), 1)) {
        if (__builtin_expect(PyTuple_GET_SIZE(obj) == 2, 1)) {
            PyObject* p0 = PyTuple_GET_ITEM(obj, 0);
            PyObject* p1 = PyTuple_GET_ITEM(obj, 1);
            double d0, d1;
            if (__builtin_expect(extract_double(p0, d0) && extract_double(p1, d1), 1)) {
                return {d0, d1};
            }
        }
    } else if (PyList_CheckExact(obj)) {
        if (PyList_GET_SIZE(obj) == 2) {
            PyObject* p0 = PyList_GET_ITEM(obj, 0);
            PyObject* p1 = PyList_GET_ITEM(obj, 1);
            double d0, d1;
            if (__builtin_expect(extract_double(p0, d0) && extract_double(p1, d1), 1)) {
                return {d0, d1};
            }
        }
    } else if (PyTuple_Check(obj)) {
        if (PyTuple_GET_SIZE(obj) == 2) {
            PyObject* p0 = PyTuple_GET_ITEM(obj, 0);
            PyObject* p1 = PyTuple_GET_ITEM(obj, 1);
            double d0, d1;
            if (extract_double(p0, d0) && extract_double(p1, d1)) {
                return {d0, d1};
            }
        }
    } else if (PyList_Check(obj)) {
        if (PyList_GET_SIZE(obj) == 2) {
            PyObject* p0 = PyList_GET_ITEM(obj, 0);
            PyObject* p1 = PyList_GET_ITEM(obj, 1);
            double d0, d1;
            if (extract_double(p0, d0) && extract_double(p1, d1)) {
                return {d0, d1};
            }
        }
    }
    return nb::cast<std::pair<double, double>>(h);
}

inline bool extract_geo_points(
    PyObject* points_obj,
    std::vector<GeoPointInternal>& pts,
    std::vector<std::pair<double, double>>& orig
) {
    if (!points_obj) return false;
    Py_ssize_t n = 0;
    PyObject* const* items = nullptr;
    if (PyList_CheckExact(points_obj) || PyList_Check(points_obj)) {
        n = PyList_GET_SIZE(points_obj);
        if (n == 0) throw std::invalid_argument("Cannot build GeoKDTree from empty point list");
        items = PySequence_Fast_ITEMS(points_obj);
    } else if (PyTuple_CheckExact(points_obj) || PyTuple_Check(points_obj)) {
        n = PyTuple_GET_SIZE(points_obj);
        if (n == 0) throw std::invalid_argument("Cannot build GeoKDTree from empty point list");
        items = &PyTuple_GET_ITEM(points_obj, 0);
    } else {
        return false;
    }

    pts.resize(n);
    orig.resize(n);
    constexpr double PI = 3.14159265358979323846;
    constexpr double DEG_TO_RAD = PI / 180.0;

    for (Py_ssize_t i = 0; i < n; ++i) {
        PyObject* item = items[i];
        double lat, lon;
        if (__builtin_expect(PyTuple_CheckExact(item) && PyTuple_GET_SIZE(item) == 2, 1)) {
            PyObject* p0 = PyTuple_GET_ITEM(item, 0);
            PyObject* p1 = PyTuple_GET_ITEM(item, 1);
            if (__builtin_expect(extract_double(p0, lat) && extract_double(p1, lon), 1)) {
                double lat_rad = lat * DEG_TO_RAD, lon_rad = lon * DEG_TO_RAD;
                double cos_lat = std::cos(lat_rad);
                pts[i] = {cos_lat * std::cos(lon_rad), cos_lat * std::sin(lon_rad), std::sin(lat_rad), lat, lon, static_cast<int>(i)};
                orig[i] = {lat, lon};
                continue;
            }
        } else if (PyList_CheckExact(item) && PyList_GET_SIZE(item) == 2) {
            PyObject* p0 = PyList_GET_ITEM(item, 0);
            PyObject* p1 = PyList_GET_ITEM(item, 1);
            if (__builtin_expect(extract_double(p0, lat) && extract_double(p1, lon), 1)) {
                double lat_rad = lat * DEG_TO_RAD, lon_rad = lon * DEG_TO_RAD;
                double cos_lat = std::cos(lat_rad);
                pts[i] = {cos_lat * std::cos(lon_rad), cos_lat * std::sin(lon_rad), std::sin(lat_rad), lat, lon, static_cast<int>(i)};
                orig[i] = {lat, lon};
                continue;
            }
        }
        try {
            auto p = parse_point2d(nb::handle(item));
            lat = p.first;
            lon = p.second;
            double lat_rad = lat * DEG_TO_RAD, lon_rad = lon * DEG_TO_RAD;
            double cos_lat = std::cos(lat_rad);
            pts[i] = {cos_lat * std::cos(lon_rad), cos_lat * std::sin(lon_rad), std::sin(lat_rad), lat, lon, static_cast<int>(i)};
            orig[i] = {lat, lon};
        } catch (...) {
            return false;
        }
    }
    return true;
}

inline bool extract_kd_points_2d(
    PyObject* points_obj,
    std::vector<KDPoint2D>& pts
) {
    if (!points_obj) return false;
    Py_ssize_t n = 0;
    PyObject* const* items = nullptr;
    if (PyList_CheckExact(points_obj) || PyList_Check(points_obj)) {
        n = PyList_GET_SIZE(points_obj);
        if (n == 0) throw std::invalid_argument("Cannot build KDTree from empty point list");
        items = PySequence_Fast_ITEMS(points_obj);
    } else if (PyTuple_CheckExact(points_obj) || PyTuple_Check(points_obj)) {
        n = PyTuple_GET_SIZE(points_obj);
        if (n == 0) throw std::invalid_argument("Cannot build KDTree from empty point list");
        items = &PyTuple_GET_ITEM(points_obj, 0);
    } else {
        return false;
    }

    pts.resize(n);
    for (Py_ssize_t i = 0; i < n; ++i) {
        PyObject* item = items[i];
        double x, y;
        if (__builtin_expect(PyTuple_CheckExact(item) && PyTuple_GET_SIZE(item) == 2, 1)) {
            PyObject* p0 = PyTuple_GET_ITEM(item, 0);
            PyObject* p1 = PyTuple_GET_ITEM(item, 1);
            if (__builtin_expect(extract_double(p0, x) && extract_double(p1, y), 1)) {
                pts[i] = {x, y, static_cast<int>(i)};
                continue;
            }
        } else if (PyList_CheckExact(item) && PyList_GET_SIZE(item) == 2) {
            PyObject* p0 = PyList_GET_ITEM(item, 0);
            PyObject* p1 = PyList_GET_ITEM(item, 1);
            if (__builtin_expect(extract_double(p0, x) && extract_double(p1, y), 1)) {
                pts[i] = {x, y, static_cast<int>(i)};
                continue;
            }
        }
        try {
            auto p = parse_point2d(nb::handle(item));
            pts[i] = {p.first, p.second, static_cast<int>(i)};
        } catch (...) {
            return false;
        }
    }
    return true;
}

template <typename F>
inline nb::dict make_quad_dict(const int best_indices[4], F&& get_val) {
    nb::dict d;
    static const char* keys[4] = {"ne", "nw", "se", "sw"};
    for (int i = 0; i < 4; ++i) {
        if (best_indices[i] >= 0) {
            d[keys[i]] = get_val(best_indices[i]);
        } else {
            d[keys[i]] = nb::none();
        }
    }
    return d;
}
}  // namespace

NB_MODULE(cpp, m) {
    m.doc() = "KD-Tree implementation for efficient nearest neighbor search";

    // ClosestPointResult struct
    nb::class_<ClosestPointResult>(m, "ClosestPointResult")
        .def_ro("point", &ClosestPointResult::point, "The closest point")
        .def_ro("distance", &ClosestPointResult::distance, "The squared distance to the closest point")
        .def("__repr__", [](const ClosestPointResult& r) {
            std::string s = "[";
            for (size_t i = 0; i < r.point.size(); ++i) {
                if (i > 0) s += ", ";
                s += std::to_string(r.point[i]);
            }
            s += "]";
            return "ClosestPointResult(point=" + s + ", distance=" + std::to_string(r.distance) + ")";
        });

    // ClosestIdxResult struct
    nb::class_<ClosestIdxResult>(m, "ClosestIdxResult")
        .def_ro("idx", &ClosestIdxResult::idx, "The index of the closest point")
        .def_ro("distance", &ClosestIdxResult::distance, "The squared distance to the closest point")
        .def("__repr__", [](const ClosestIdxResult& r) {
            return "ClosestIdxResult(idx=" + std::to_string(r.idx) + ", distance=" + std::to_string(r.distance) + ")";
        });

    // KDTree class
    nb::class_<KDTree>(m, "KDTree")
        .def("__init__", [](KDTree* t, nb::handle points_handle) {
            std::vector<KDPoint2D> pts2d;
            if (extract_kd_points_2d(points_handle.ptr(), pts2d)) {
                new (t) KDTree(std::move(pts2d));
                return;
            }
            auto points = nb::cast<std::vector<std::vector<double>>>(points_handle);
            new (t) KDTree(points);
        }, nb::arg("points"), "Build a KD-Tree from a list of points")
        .def("closest_point", [](const KDTree& self, nb::handle point_handle) {
            if (self.get_dimensions() == 2) {
                try {
                    auto p = parse_point2d(point_handle);
                    auto res = self.closest_point_2d(p.first, p.second);
                    return nb::make_tuple(res.first, res.second);
                } catch (...) {}
            }
            std::vector<double> pt = nb::cast<std::vector<double>>(point_handle);
            auto res = self.closest_point(pt);
            nb::list out;
            for (double v : res) out.append(v);
            return nb::tuple(out);
        }, nb::arg("point"), "Find the closest point to the given point")
        .def("closest_point_per_quadrant", [](const KDTree& self, nb::handle point_handle) {
            if (self.get_dimensions() != 2) {
                throw std::invalid_argument("closest_point_per_quadrant is only supported for 2D Cartesian points.");
            }
            auto p = parse_point2d(point_handle);
            int best_indices[4];
            self.closest_point_per_quadrant_2d_raw(p.first, p.second, best_indices);
            return make_quad_dict(best_indices, [&](int idx) {
                const auto& pt = self.get_node_2d(idx);
                return nb::make_tuple(pt.x, pt.y);
            });
        }, nb::arg("point"), "Find the closest point in each quadrant ('ne', 'nw', 'se', 'sw')");

    // GeoKDTree class
    nb::class_<GeoKDTree>(m, "GeoKDTree")
        .def("__init__", [](GeoKDTree* t, nb::handle points_handle) {
            std::vector<GeoPointInternal> pts;
            std::vector<std::pair<double, double>> orig;
            if (extract_geo_points(points_handle.ptr(), pts, orig)) {
                new (t) GeoKDTree(std::move(pts), std::move(orig));
                return;
            }
            auto points = nb::cast<std::vector<std::pair<double, double>>>(points_handle);
            new (t) GeoKDTree(std::move(points));
        }, nb::arg("points"), "Build a geographic KD-Tree from a list of (latitude, longitude) pairs")
        .def("closest_idx", [](const GeoKDTree& self, nb::handle point_handle) {
            auto p = parse_point2d(point_handle);
            return self.closest_idx(p.first, p.second);
        }, nb::arg("point"), "Find the index of the closest point to the given (lat, lon) pair")
        .def("closest_point", [](const GeoKDTree& self, nb::handle point_handle) {
            auto p = parse_point2d(point_handle);
            auto res = self.closest_point(p.first, p.second);
            return nb::make_tuple(res.first, res.second);
        }, nb::arg("point"), "Find the closest point (lat, lon) to the given (lat, lon) pair")
        .def("closest_idx_per_quadrant", [](const GeoKDTree& self, nb::handle point_handle) {
            auto p = parse_point2d(point_handle);
            int best_indices[4];
            self.closest_idx_per_quadrant_raw(p.first, p.second, best_indices);
            return make_quad_dict(best_indices, [](int idx) { return nb::cast(idx); });
        }, nb::arg("point"), "Find the index of the closest point in each quadrant ('ne', 'nw', 'se', 'sw')")
        .def("closest_point_per_quadrant", [](const GeoKDTree& self, nb::handle point_handle) {
            auto p = parse_point2d(point_handle);
            int best_indices[4];
            self.closest_idx_per_quadrant_raw(p.first, p.second, best_indices);
            return make_quad_dict(best_indices, [&](int idx) {
                const auto& pt = self.get_original_point(idx);
                return nb::make_tuple(pt.first, pt.second);
            });
        }, nb::arg("point"), "Find the closest point (lat, lon) in each quadrant ('ne', 'nw', 'se', 'sw')")
        .def_static("lat_lon_idx_to_xyz_idx", &GeoKDTree::lat_lon_idx_to_xyz_idx,
             nb::arg("lat"), nb::arg("lon"), nb::arg("idx") = 0,
             "Convert latitude and longitude to Cartesian coordinates (x, y, z) with an index");

    // Helper functions
    m.def("squared_distance", &kdtree_helpers::squared_distance,
          nb::arg("p1"), nb::arg("p2"), nb::arg("axis_count") = 2,
          "Calculate squared distance between two points");
    m.def("squared_distance_3d", &kdtree_helpers::squared_distance_3d,
          nb::arg("p1"), nb::arg("p2"),
          "Calculate squared distance between two 3D points");
    m.def("lat_lon_idx_to_xyz_idx", &kdtree_helpers::lat_lon_idx_to_xyz_idx,
          nb::arg("lat"), nb::arg("lon"), nb::arg("idx") = 0,
          "Convert latitude and longitude to Cartesian coordinates");
}