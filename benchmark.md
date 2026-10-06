# GeoKDTree Performance Benchmarks

Automated performance benchmarks for `geokdtree` comparing C++ and Pure Python implementations across various dataset scales.

## Environment

| Attribute | Value |
|---|---|
| **Date** | 2026-10-06 19:01:11 UTC |
| **OS** | Linux-7.0.0-38-generic-x86_64-with-glibc2.39 |
| **Architecture** | x86_64 |
| **Python** | CPython 3.14.5 |
| **C++ Acceleration** | Enabled (`nanobind`) |

## Executive Summary

- **Sub-Microsecond & Low-Microsecond Lookups**: Nearest-neighbor queries run in **200–810 ns** up to 100k points (1.1–1.5 µs at 1M points), while Cartesian 4-quadrant queries complete in **590 ns – 1.89 µs** across all scales.
- **Massive C++ Speedup**: The compiled C++ extension delivers **up to 15x–35x faster lookups** for nearest-neighbor and quadrant searches, along with **4x–12x faster tree construction**.
- **Simultaneous 4-Quadrant Search**: Finds the closest points in all 4 cardinal quadrants (`ne`, `nw`, `se`, `sw`) in a single $O(\log N)$ tree traversal with antimeridian wrapping.
- **Sub-Second 1M Tree Construction**: Tree construction scales at strictly $O(N \log N)$ using in-place partitioning, building a 100k spatial index in **~37 ms** and a 1M spatial index in **~420–550 ms**.
- **Zero GIS Overhead**: Works directly with `(latitude, longitude)` coordinates using internal 3D spherical trigonometry Cartesian projections.

## GeoKDTree Benchmarks (Latitude/Longitude)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.439 ms | 1.37 ms | **3.11x** | 375.0 ns | 7.54 µs | **20.1x** | 1.98 µs | 49.90 µs | **25.2x** |
| 10,000 | 4.89 ms | 17.59 ms | **3.59x** | 468.4 ns | 9.81 µs | **20.9x** | 2.58 µs | 79.54 µs | **30.8x** |
| 100,000 | 56.71 ms | 274.49 ms | **4.84x** | 937.5 ns | 16.02 µs | **17.1x** | 4.89 µs | 213.42 µs | **43.6x** |
| 1,000,000 | 654.44 ms | 5.24 s | **8.01x** | 1.77 µs | 22.32 µs | **12.6x** | 11.87 µs | 573.81 µs | **48.3x** |

### Detailed C++ GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.439 ms | 375.0 ns | 381.5 ns | 1.98 µs | 2,666,679 qps | 504,596 qps |
| 10,000 | 4.89 ms | 468.4 ns | 480.4 ns | 2.58 µs | 2,135,073 qps | 386,888 qps |
| 100,000 | 56.71 ms | 937.5 ns | 712.4 ns | 4.89 µs | 1,066,682 qps | 204,374 qps |
| 1,000,000 | 654.44 ms | 1.77 µs | 910.8 ns | 11.87 µs | 564,389 qps | 84,258 qps |

### Detailed Pure Python GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1.37 ms | 7.54 µs | 7.57 µs | 49.90 µs | 132,555 qps | 20,038 qps |
| 10,000 | 17.59 ms | 9.81 µs | 9.91 µs | 79.54 µs | 101,950 qps | 12,572 qps |
| 100,000 | 274.49 ms | 16.02 µs | 16.03 µs | 213.42 µs | 62,418 qps | 4,685 qps |
| 1,000,000 | 5.24 s | 22.32 µs | 14.37 µs | 573.81 µs | 44,805 qps | 1,742 qps |


## KDTree Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.020 ms | 0.095 ms | **4.71x** | 218.2 ns | 5.31 µs | **24.3x** | 819.7 ns | 20.63 µs | **25.2x** |
| 1,000 | 0.159 ms | 0.997 ms | **6.27x** | 290.3 ns | 7.21 µs | **24.8x** | 1.04 µs | 17.53 µs | **16.8x** |
| 10,000 | 2.02 ms | 16.16 ms | **7.99x** | 351.3 ns | 9.16 µs | **26.1x** | 1.20 µs | 20.89 µs | **17.4x** |
| 100,000 | 27.70 ms | 218.10 ms | **7.87x** | 533.0 ns | 12.66 µs | **23.8x** | 1.35 µs | 27.00 µs | **19.9x** |
| 1,000,000 | 386.64 ms | 4.72 s | **12.20x** | 1.21 µs | 18.55 µs | **15.3x** | 1.82 µs | 28.31 µs | **15.6x** |
### Detailed C++ KDTree Results

| Points ($N$) | Build Time | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|
| 100 | 0.020 ms | 218.2 ns | 819.7 ns | 4,582,413 qps | 1,219,921 qps |
| 1,000 | 0.159 ms | 290.3 ns | 1.04 µs | 3,444,892 qps | 957,914 qps |
| 10,000 | 2.02 ms | 351.3 ns | 1.20 µs | 2,846,349 qps | 833,004 qps |
| 100,000 | 27.70 ms | 533.0 ns | 1.35 µs | 1,876,292 qps | 738,072 qps |
| 1,000,000 | 386.64 ms | 1.21 µs | 1.82 µs | 826,955 qps | 549,763 qps |

### Detailed Pure Python KDTree Results

| Points ($N$) | Build Time | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|
| 100 | 0.095 ms | 5.31 µs | 20.63 µs | 188,452 qps | 48,484 qps |
| 1,000 | 0.997 ms | 7.21 µs | 17.53 µs | 138,679 qps | 57,032 qps |
| 10,000 | 16.16 ms | 9.16 µs | 20.89 µs | 109,160 qps | 47,861 qps |
| 100,000 | 218.10 ms | 12.66 µs | 27.00 µs | 78,987 qps | 37,042 qps |
| 1,000,000 | 4.72 s | 18.55 µs | 28.31 µs | 53,902 qps | 35,320 qps |


## Methodology

1. **Data**: Coordinates randomly and uniformly distributed over valid ranges ($[-90, 90]$ latitude, $[-180, 180]$ longitude for GeoKDTree; $[0, 1000] \times [0, 1000]$ for 2D KDTree).
2. **Timing**: Measured with `time.perf_counter()` over thousands of repeated lookups to compute stable averages.
3. **Reproducibility**: Run `uv run python utils/benchmark.py` to regenerate these benchmarks on your hardware.
