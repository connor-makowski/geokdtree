#include <nanobind/nanobind.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/pair.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/optional.h>
#include <nanobind/stl/unordered_map.h>
#include <string>
#include <utility>
#include "../src/geokdtree.hpp"
#include "../src/hilbert.hpp"

namespace nb = nanobind;

#if defined(__GNUC__) || defined(__clang__)
#  define GEOKDTREE_LIKELY(x)   __builtin_expect(!!(x), 1)
#  define GEOKDTREE_UNLIKELY(x) __builtin_expect(!!(x), 0)
#else
#  define GEOKDTREE_LIKELY(x)   (x)
#  define GEOKDTREE_UNLIKELY(x) (x)
#endif

namespace {
inline bool extract_double(PyObject* obj, double& out) noexcept {
    if (GEOKDTREE_LIKELY(PyFloat_CheckExact(obj))) {
        out = PyFloat_AS_DOUBLE(obj);
        return true;
    }
    if (GEOKDTREE_UNLIKELY(PyBool_Check(obj))) return false;
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
    if (GEOKDTREE_LIKELY(PyTuple_CheckExact(obj))) {
        if (GEOKDTREE_LIKELY(PyTuple_GET_SIZE(obj) == 2)) {
            PyObject* p0 = PyTuple_GET_ITEM(obj, 0);
            PyObject* p1 = PyTuple_GET_ITEM(obj, 1);
            double d0, d1;
            if (GEOKDTREE_LIKELY(extract_double(p0, d0) && extract_double(p1, d1))) {
                return {d0, d1};
            }
        }
    } else if (PyList_CheckExact(obj)) {
        if (PyList_GET_SIZE(obj) == 2) {
            PyObject* p0 = PyList_GET_ITEM(obj, 0);
            PyObject* p1 = PyList_GET_ITEM(obj, 1);
            double d0, d1;
            if (GEOKDTREE_LIKELY(extract_double(p0, d0) && extract_double(p1, d1))) {
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
        if (GEOKDTREE_LIKELY(PyTuple_CheckExact(item) && PyTuple_GET_SIZE(item) == 2)) {
            PyObject* p0 = PyTuple_GET_ITEM(item, 0);
            PyObject* p1 = PyTuple_GET_ITEM(item, 1);
            if (GEOKDTREE_LIKELY(extract_double(p0, lat) && extract_double(p1, lon))) {
                double lat_rad = lat * DEG_TO_RAD, lon_rad = lon * DEG_TO_RAD;
                double cos_lat = std::cos(lat_rad);
                pts[i] = {cos_lat * std::cos(lon_rad), cos_lat * std::sin(lon_rad), std::sin(lat_rad), lat, lon, static_cast<int>(i)};
                orig[i] = {lat, lon};
                continue;
            }
        } else if (PyList_CheckExact(item) && PyList_GET_SIZE(item) == 2) {
            PyObject* p0 = PyList_GET_ITEM(item, 0);
            PyObject* p1 = PyList_GET_ITEM(item, 1);
            if (GEOKDTREE_LIKELY(extract_double(p0, lat) && extract_double(p1, lon))) {
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
        if (GEOKDTREE_LIKELY(PyTuple_CheckExact(item) && PyTuple_GET_SIZE(item) == 2)) {
            PyObject* p0 = PyTuple_GET_ITEM(item, 0);
            PyObject* p1 = PyTuple_GET_ITEM(item, 1);
            if (GEOKDTREE_LIKELY(extract_double(p0, x) && extract_double(p1, y))) {
                pts[i] = {x, y, static_cast<int>(i)};
                continue;
            }
        } else if (PyList_CheckExact(item) && PyList_GET_SIZE(item) == 2) {
            PyObject* p0 = PyList_GET_ITEM(item, 0);
            PyObject* p1 = PyList_GET_ITEM(item, 1);
            if (GEOKDTREE_LIKELY(extract_double(p0, x) && extract_double(p1, y))) {
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

// Validate a complete batch before entering the existing scalar search.
inline std::vector<std::vector<double>> validate_points(
    nb::handle queries, int dimensions
) {
    std::vector<std::vector<double>> points;
    for (nb::handle query : nb::borrow<nb::iterable>(queries)) {
        auto point = nb::cast<std::vector<double>>(query);
        if (point.size() != static_cast<size_t>(dimensions))
            throw std::invalid_argument("query dimensions must match tree dimensions");
        for (double value : point)
            if (!std::isfinite(value))
                throw std::invalid_argument("query coordinates must be finite");
        points.push_back(std::move(point));
    }
    return points;
}

inline bool extract_nd_points(
    PyObject* points_obj,
    std::vector<std::vector<double>>& pts
) {
    if (!points_obj) return false;
    Py_ssize_t n = 0;
    PyObject* const* items = nullptr;
    if (PyList_CheckExact(points_obj) || PyList_Check(points_obj)) {
        n = PyList_GET_SIZE(points_obj);
        if (n == 0) { pts.clear(); return true; }
        items = PySequence_Fast_ITEMS(points_obj);
    } else if (PyTuple_CheckExact(points_obj) || PyTuple_Check(points_obj)) {
        n = PyTuple_GET_SIZE(points_obj);
        if (n == 0) { pts.clear(); return true; }
        items = &PyTuple_GET_ITEM(points_obj, 0);
    } else {
        return false;
    }

    pts.resize(n);
    Py_ssize_t dims = -1;
    for (Py_ssize_t i = 0; i < n; ++i) {
        PyObject* item = items[i];
        Py_ssize_t d = 0;
        PyObject* const* coord_items = nullptr;
        if (PyTuple_CheckExact(item) || PyTuple_Check(item)) {
            d = PyTuple_GET_SIZE(item);
            if (d == 0) throw std::invalid_argument("points must have at least one dimension");
            coord_items = &PyTuple_GET_ITEM(item, 0);
        } else if (PyList_CheckExact(item) || PyList_Check(item)) {
            d = PyList_GET_SIZE(item);
            if (d == 0) throw std::invalid_argument("points must have at least one dimension");
            coord_items = PySequence_Fast_ITEMS(item);
        } else {
            return false;
        }

        if (dims == -1) {
            dims = d;
        } else if (d != dims) {
            throw std::invalid_argument("all points must have the same dimension");
        }

        pts[i].resize(dims);
        for (Py_ssize_t j = 0; j < dims; ++j) {
            double v;
            if (!extract_double(coord_items[j], v)) return false;
            if (!std::isfinite(v)) throw std::invalid_argument("coordinates must be finite");
            pts[i][j] = v;
        }
    }
    return true;
}

inline bool extract_geo_points_allow_empty(
    PyObject* points_obj,
    std::vector<std::pair<double, double>>& orig
) {
    if (!points_obj) return false;
    Py_ssize_t n = 0;
    PyObject* const* items = nullptr;
    if (PyList_CheckExact(points_obj) || PyList_Check(points_obj)) {
        n = PyList_GET_SIZE(points_obj);
        if (n == 0) { orig.clear(); return true; }
        items = PySequence_Fast_ITEMS(points_obj);
    } else if (PyTuple_CheckExact(points_obj) || PyTuple_Check(points_obj)) {
        n = PyTuple_GET_SIZE(points_obj);
        if (n == 0) { orig.clear(); return true; }
        items = &PyTuple_GET_ITEM(points_obj, 0);
    } else {
        return false;
    }

    orig.resize(n);
    for (Py_ssize_t i = 0; i < n; ++i) {
        PyObject* item = items[i];
        double lat, lon;
        if (GEOKDTREE_LIKELY(PyTuple_CheckExact(item) && PyTuple_GET_SIZE(item) == 2)) {
            PyObject* p0 = PyTuple_GET_ITEM(item, 0);
            PyObject* p1 = PyTuple_GET_ITEM(item, 1);
            if (GEOKDTREE_LIKELY(extract_double(p0, lat) && extract_double(p1, lon))) {
                if (!std::isfinite(lat) || !std::isfinite(lon))
                    throw std::invalid_argument("coordinates must be finite");
                orig[i] = {lat, lon};
                continue;
            }
        } else if (PyList_CheckExact(item) && PyList_GET_SIZE(item) == 2) {
            PyObject* p0 = PyList_GET_ITEM(item, 0);
            PyObject* p1 = PyList_GET_ITEM(item, 1);
            if (GEOKDTREE_LIKELY(extract_double(p0, lat) && extract_double(p1, lon))) {
                if (!std::isfinite(lat) || !std::isfinite(lon))
                    throw std::invalid_argument("coordinates must be finite");
                orig[i] = {lat, lon};
                continue;
            }
        }
        try {
            auto p = parse_point2d(nb::handle(item));
            if (!std::isfinite(p.first) || !std::isfinite(p.second))
                throw std::invalid_argument("coordinates must be finite");
            orig[i] = p;
        } catch (...) {
            return false;
        }
    }
    return true;
}

inline std::pair<double, double> parse_geo_query(nb::handle point_handle) {
    PyObject* obj = point_handle.ptr();
    if (GEOKDTREE_LIKELY(PyTuple_CheckExact(obj))) {
        if (GEOKDTREE_LIKELY(PyTuple_GET_SIZE(obj) == 2)) {
            double d0, d1;
            if (GEOKDTREE_LIKELY(extract_double(PyTuple_GET_ITEM(obj, 0), d0) && extract_double(PyTuple_GET_ITEM(obj, 1), d1))) {
                if (GEOKDTREE_LIKELY(std::isfinite(d0) && std::isfinite(d1))) {
                    return {d0, d1};
                }
                throw std::invalid_argument("query coordinates must be finite");
            }
            throw nb::type_error("coordinates must be numeric");
        }
        throw std::invalid_argument("query dimensions must match tree dimensions");
    }
    if (PyList_CheckExact(obj)) {
        if (PyList_GET_SIZE(obj) == 2) {
            double d0, d1;
            if (extract_double(PyList_GET_ITEM(obj, 0), d0) && extract_double(PyList_GET_ITEM(obj, 1), d1)) {
                if (std::isfinite(d0) && std::isfinite(d1)) return {d0, d1};
                throw std::invalid_argument("query coordinates must be finite");
            }
            throw nb::type_error("coordinates must be numeric");
        }
        throw std::invalid_argument("query dimensions must match tree dimensions");
    }
    if (PyTuple_Check(obj)) {
        if (PyTuple_GET_SIZE(obj) != 2)
            throw std::invalid_argument("query dimensions must match tree dimensions");
        double d0, d1;
        if (!extract_double(PyTuple_GET_ITEM(obj, 0), d0) || !extract_double(PyTuple_GET_ITEM(obj, 1), d1))
            throw nb::type_error("coordinates must be numeric");
        if (!std::isfinite(d0) || !std::isfinite(d1))
            throw std::invalid_argument("query coordinates must be finite");
        return {d0, d1};
    } else if (PyList_Check(obj)) {
        if (PyList_GET_SIZE(obj) != 2)
            throw std::invalid_argument("query dimensions must match tree dimensions");
        double d0, d1;
        if (!extract_double(PyList_GET_ITEM(obj, 0), d0) || !extract_double(PyList_GET_ITEM(obj, 1), d1))
            throw nb::type_error("coordinates must be numeric");
        if (!std::isfinite(d0) || !std::isfinite(d1))
            throw std::invalid_argument("query coordinates must be finite");
        return {d0, d1};
    }
    return parse_point2d(point_handle);
}

inline std::vector<double> parse_nd_query(nb::handle point_handle, int expected_dims) {
    PyObject* obj = point_handle.ptr();
    Py_ssize_t n = 0;
    PyObject* const* items = nullptr;
    if (PyTuple_Check(obj)) {
        n = PyTuple_GET_SIZE(obj);
        items = &PyTuple_GET_ITEM(obj, 0);
    } else if (PyList_Check(obj)) {
        n = PyList_GET_SIZE(obj);
        items = PySequence_Fast_ITEMS(obj);
    } else {
        auto vec = nb::cast<std::vector<double>>(point_handle);
        if (expected_dims > 0 && static_cast<int>(vec.size()) != expected_dims)
            throw std::invalid_argument("query dimensions must match tree dimensions");
        for (double v : vec) {
            if (!std::isfinite(v))
                throw std::invalid_argument("query coordinates must be finite");
        }
        return vec;
    }
    if (expected_dims > 0 && n != expected_dims)
        throw std::invalid_argument("query dimensions must match tree dimensions");
    std::vector<double> res(n);
    for (Py_ssize_t i = 0; i < n; ++i) {
        double v;
        if (!extract_double(items[i], v))
            throw nb::type_error("coordinates must be numeric");
        if (!std::isfinite(v))
            throw std::invalid_argument("query coordinates must be finite");
        res[i] = v;
    }
    return res;
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
        .def("closest_points", [](const KDTree& self, nb::handle points_handle) {
            auto points = validate_points(points_handle, self.get_dimensions());
            nb::list out;
            for (const auto& point : points)
                out.append(nb::tuple(nb::cast(self.closest_point(point))));
            return out;
        }, nb::arg("points"), "Return nearest points in query order")
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
        .def("closest_indices", [](const GeoKDTree& self, nb::handle points_handle) {
            auto points = validate_points(points_handle, 2);
            nb::list out;
            for (const auto& point : points)
                out.append(self.closest_idx(point[0], point[1]));
            return out;
        }, nb::arg("points"), "Return original dataset indices in query order")
        .def("closest_indicies", [](const GeoKDTree& self, nb::handle points_handle) {
            auto points = validate_points(points_handle, 2);
            nb::list out;
            for (const auto& point : points)
                out.append(self.closest_idx(point[0], point[1]));
            return out;
        }, nb::arg("points"), "Return original dataset indices in query order")
        .def("closest_points", [](const GeoKDTree& self, nb::handle points_handle) {
            auto points = validate_points(points_handle, 2);
            nb::list out;
            for (const auto& point : points) {
                auto result = self.closest_point(point[0], point[1]);
                out.append(nb::make_tuple(result.first, result.second));
            }
            return out;
        }, nb::arg("points"), "Return nearest geographic points in query order")
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

    m.def("hilbert_index", [](nb::handle coordinates, nb::handle bits_handle) -> nb::object {
        nb::object module = nb::module_::import_("geokdtree.hilbert");
        nb::tuple point = nb::tuple(coordinates);
        nb::object validated = module.attr("hilbert_index")(point, nb::arg("bits") = bits_handle);
        int bits = nb::cast<int>(module.attr("_positive")(bits_handle, "bits"));
        if (point.size() > static_cast<size_t>(64 / std::min(bits, 65))) return validated;
        return nb::cast(hilbert_helpers::index(nb::cast<std::vector<uint64_t>>(point), bits));
    }, nb::arg("coordinates"), nb::kw_only(), nb::arg("bits"));
    m.def("hilbert_coordinates", [](nb::handle index, nb::handle dimensions, nb::handle bits_handle) -> nb::object {
        nb::object module = nb::module_::import_("geokdtree.hilbert");
        nb::object validated = module.attr("hilbert_coordinates")(index, nb::arg("dimensions") = dimensions, nb::arg("bits") = bits_handle);
        int bits = nb::cast<int>(module.attr("_positive")(bits_handle, "bits"));
        int dims = nb::cast<int>(module.attr("_positive")(dimensions, "dimensions"));
        if (dims > 64 / std::min(bits, 65)) return validated;
        return nb::tuple(nb::cast(hilbert_helpers::coordinates(nb::cast<uint64_t>(index), dims, bits)));
    }, nb::arg("index"), nb::kw_only(), nb::arg("dimensions"), nb::arg("bits"));

    nb::class_<NativeHilbert>(m, "Hilbert")
        .def("__init__", [](NativeHilbert* t, nb::handle points_handle, nb::handle bits_handle, nb::handle bounds_handle) {
            int bits = 16;
            if (!bits_handle.is_none()) {
                bits = nb::cast<int>(bits_handle);
            }
            std::optional<std::vector<std::pair<double, double>>> bounds;
            if (!bounds_handle.is_none()) {
                bounds = nb::cast<std::vector<std::pair<double, double>>>(bounds_handle);
            }
            std::vector<std::vector<double>> pts;
            if (points_handle.is_valid() && !points_handle.is_none()) {
                if (!extract_nd_points(points_handle.ptr(), pts)) {
                    pts = nb::cast<std::vector<std::vector<double>>>(points_handle);
                }
            }
            new (t) NativeHilbert(std::move(pts), bits, bounds);
        }, nb::arg("points") = nb::tuple(), nb::arg("bits") = 16, nb::arg("bounds") = nb::none(),
           "Build a Hilbert spatial index from a list of N-dimensional Cartesian points")
        .def_ro("dimensions", &NativeHilbert::dimensions)
        .def_ro("axis_count", &NativeHilbert::dimensions)
        .def_ro("bits", &NativeHilbert::bits)
        .def_prop_ro("bounds", [](const NativeHilbert& self) {
            nb::list b_list;
            for (const auto& b : self.bounds) {
                b_list.append(nb::make_tuple(b.first, b.second));
            }
            return nb::tuple(b_list);
        })
        .def_prop_ro("order", [](const NativeHilbert& self) {
            nb::list o_list;
            for (size_t idx : self.order) {
                o_list.append(idx);
            }
            return o_list;
        })
        .def("__len__", &NativeHilbert::size)
        .def("hilbert_order", [](const NativeHilbert& self) {
            nb::list o_list;
            for (size_t idx : self.order) {
                o_list.append(idx);
            }
            return o_list;
        })
        .def("closest_idx", [](const NativeHilbert& self, nb::handle point_handle) {
            auto pt = parse_nd_query(point_handle, self.dimensions);
            return self.closest_idx(pt);
        }, nb::arg("point"), "Find the index of the closest point in the Hilbert index")
        .def("closest_point", [](const NativeHilbert& self, nb::handle point_handle) {
            auto pt = parse_nd_query(point_handle, self.dimensions);
            auto res = self.closest_point(pt);
            nb::list out;
            for (double v : res) out.append(v);
            return nb::tuple(out);
        }, nb::arg("point"), "Find the closest point in the Hilbert index")
        .def("closest_indices", [](const NativeHilbert& self, nb::handle points_handle) {
            auto points = validate_points(points_handle, self.dimensions);
            if (points.empty()) return nb::list();
            if (self.size() == 0) throw std::invalid_argument("tree is empty");
            nb::list out;
            for (const auto& point : points) {
                out.append(self.closest_idx(point));
            }
            return out;
        }, nb::arg("points"), "Return original dataset indices in query order")
        .def("closest_indicies", [](const NativeHilbert& self, nb::handle points_handle) {
            auto points = validate_points(points_handle, self.dimensions);
            if (points.empty()) return nb::list();
            if (self.size() == 0) throw std::invalid_argument("tree is empty");
            nb::list out;
            for (const auto& point : points) {
                out.append(self.closest_idx(point));
            }
            return out;
        }, nb::arg("points"), "Return original dataset indices in query order")
        .def("closest_points", [](const NativeHilbert& self, nb::handle points_handle) {
            auto points = validate_points(points_handle, self.dimensions);
            if (points.empty()) return nb::list();
            if (self.size() == 0) throw std::invalid_argument("tree is empty");
            nb::list out;
            for (const auto& point : points) {
                auto res = self.closest_point(point);
                nb::list p_out;
                for (double v : res) p_out.append(v);
                out.append(nb::tuple(p_out));
            }
            return out;
        }, nb::arg("points"), "Return closest points in query order")
        .def("closest_hilbert_idx", [](const NativeHilbert& self, nb::handle point_handle) {
            auto pt = parse_nd_query(point_handle, self.dimensions);
            return self.closest_idx(pt);
        }, nb::arg("point"))
        .def("closest_hilbert_point", [](const NativeHilbert& self, nb::handle point_handle) {
            auto pt = parse_nd_query(point_handle, self.dimensions);
            auto res = self.closest_point(pt);
            nb::list out;
            for (double v : res) out.append(v);
            return nb::tuple(out);
        }, nb::arg("point"))
        .def("closest_hilbert_indices", [](const NativeHilbert& self, nb::handle points_handle) {
            auto points = validate_points(points_handle, self.dimensions);
            if (points.empty()) return nb::list();
            if (self.size() == 0) throw std::invalid_argument("tree is empty");
            nb::list out;
            for (const auto& point : points) {
                out.append(self.closest_idx(point));
            }
            return out;
        }, nb::arg("points"))
        .def("closest_hilbert_indicies", [](const NativeHilbert& self, nb::handle points_handle) {
            auto points = validate_points(points_handle, self.dimensions);
            if (points.empty()) return nb::list();
            if (self.size() == 0) throw std::invalid_argument("tree is empty");
            nb::list out;
            for (const auto& point : points) {
                out.append(self.closest_idx(point));
            }
            return out;
        }, nb::arg("points"))
        .def("closest_hilbert_points", [](const NativeHilbert& self, nb::handle points_handle) {
            auto points = validate_points(points_handle, self.dimensions);
            if (points.empty()) return nb::list();
            if (self.size() == 0) throw std::invalid_argument("tree is empty");
            nb::list out;
            for (const auto& point : points) {
                auto res = self.closest_point(point);
                nb::list p_out;
                for (double v : res) p_out.append(v);
                out.append(nb::tuple(p_out));
            }
            return out;
        }, nb::arg("points"));

    nb::class_<NativeGeoHilbert>(m, "GeoHilbert")
        .def("__init__", [](NativeGeoHilbert* t, nb::handle points_handle, nb::handle bits_handle) {
            int bits = 21;
            if (!bits_handle.is_none()) {
                bits = nb::cast<int>(bits_handle);
            }
            std::vector<std::pair<double, double>> orig;
            if (points_handle.is_valid() && !points_handle.is_none()) {
                if (!extract_geo_points_allow_empty(points_handle.ptr(), orig)) {
                    orig = nb::cast<std::vector<std::pair<double, double>>>(points_handle);
                }
            }
            new (t) NativeGeoHilbert(std::move(orig), bits);
        }, nb::arg("points") = nb::tuple(), nb::arg("bits") = 21,
           "Build a GeoHilbert spatial index from a list of (latitude, longitude) pairs")
        .def_ro("bits", &NativeGeoHilbert::bits)
        .def_prop_ro("order", [](const NativeGeoHilbert& self) {
            nb::list o_list;
            for (size_t idx : self.order) {
                o_list.append(idx);
            }
            return o_list;
        })
        .def("__len__", &NativeGeoHilbert::size)
        .def("hilbert_order", [](const NativeGeoHilbert& self) {
            nb::list o_list;
            for (size_t idx : self.order) {
                o_list.append(idx);
            }
            return o_list;
        })
        .def("closest_idx", [](const NativeGeoHilbert& self, nb::handle point_handle) {
            auto p = parse_geo_query(point_handle);
            return self.closest_idx(p.first, p.second);
        }, nb::arg("point"), "Find the index of the closest point to the given (lat, lon) pair")
        .def("closest_point", [](const NativeGeoHilbert& self, nb::handle point_handle) {
            auto p = parse_geo_query(point_handle);
            auto res = self.closest_point(p.first, p.second);
            return nb::make_tuple(res.first, res.second);
        }, nb::arg("point"), "Find the closest point (lat, lon) to the given (lat, lon) pair")
        .def("closest_indices", [](const NativeGeoHilbert& self, nb::handle points_handle) {
            auto points = validate_points(points_handle, 2);
            if (points.empty()) return nb::list();
            if (self.size() == 0) throw std::invalid_argument("tree is empty");
            nb::list out;
            for (const auto& point : points) {
                out.append(self.closest_idx(point[0], point[1]));
            }
            return out;
        }, nb::arg("points"), "Return original dataset indices in query order")
        .def("closest_indicies", [](const NativeGeoHilbert& self, nb::handle points_handle) {
            auto points = validate_points(points_handle, 2);
            if (points.empty()) return nb::list();
            if (self.size() == 0) throw std::invalid_argument("tree is empty");
            nb::list out;
            for (const auto& point : points) {
                out.append(self.closest_idx(point[0], point[1]));
            }
            return out;
        }, nb::arg("points"), "Return original dataset indices in query order")
        .def("closest_points", [](const NativeGeoHilbert& self, nb::handle points_handle) {
            auto points = validate_points(points_handle, 2);
            if (points.empty()) return nb::list();
            if (self.size() == 0) throw std::invalid_argument("tree is empty");
            nb::list out;
            for (const auto& point : points) {
                auto res = self.closest_point(point[0], point[1]);
                out.append(nb::make_tuple(res.first, res.second));
            }
            return out;
        }, nb::arg("points"), "Return closest (lat, lon) points in query order")
        .def("closest_hilbert_idx", [](const NativeGeoHilbert& self, nb::handle point_handle) {
            auto p = parse_geo_query(point_handle);
            return self.closest_idx(p.first, p.second);
        }, nb::arg("point"))
        .def("closest_hilbert_point", [](const NativeGeoHilbert& self, nb::handle point_handle) {
            auto p = parse_geo_query(point_handle);
            auto res = self.closest_point(p.first, p.second);
            return nb::make_tuple(res.first, res.second);
        }, nb::arg("point"))
        .def("closest_hilbert_indices", [](const NativeGeoHilbert& self, nb::handle points_handle) {
            auto points = validate_points(points_handle, 2);
            if (points.empty()) return nb::list();
            if (self.size() == 0) throw std::invalid_argument("tree is empty");
            nb::list out;
            for (const auto& point : points) {
                out.append(self.closest_idx(point[0], point[1]));
            }
            return out;
        }, nb::arg("points"))
        .def("closest_hilbert_indicies", [](const NativeGeoHilbert& self, nb::handle points_handle) {
            auto points = validate_points(points_handle, 2);
            if (points.empty()) return nb::list();
            if (self.size() == 0) throw std::invalid_argument("tree is empty");
            nb::list out;
            for (const auto& point : points) {
                out.append(self.closest_idx(point[0], point[1]));
            }
            return out;
        }, nb::arg("points"))
        .def("closest_hilbert_points", [](const NativeGeoHilbert& self, nb::handle points_handle) {
            auto points = validate_points(points_handle, 2);
            if (points.empty()) return nb::list();
            if (self.size() == 0) throw std::invalid_argument("tree is empty");
            nb::list out;
            for (const auto& point : points) {
                auto res = self.closest_point(point[0], point[1]);
                out.append(nb::make_tuple(res.first, res.second));
            }
            return out;
        }, nb::arg("points"));

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