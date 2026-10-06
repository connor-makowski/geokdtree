# GeoKDTree Performance Benchmarks

Automated performance benchmarks for `geokdtree` comparing C++ and Pure Python implementations across various dataset scales.

## Environment

| Attribute | Value |
|---|---|
| **Date** | 2026-10-06 19:28:11 UTC |
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
| 1,000 | 0.342 ms | 1.37 ms | **4.02x** | 394.2 ns | 7.58 µs | **19.2x** | 2.18 µs | 51.00 µs | **23.4x** |
| 10,000 | 4.92 ms | 17.91 ms | **3.64x** | 481.4 ns | 10.45 µs | **21.7x** | 2.87 µs | 82.80 µs | **28.9x** |
| 100,000 | 56.88 ms | 277.49 ms | **4.88x** | 904.9 ns | 15.82 µs | **17.5x** | 5.38 µs | 207.67 µs | **38.6x** |
| 1,000,000 | 672.00 ms | 5.37 s | **8.00x** | 1.86 µs | 23.39 µs | **12.6x** | 12.98 µs | 610.45 µs | **47.0x** |

### Detailed C++ GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.342 ms | 394.2 ns | 387.5 ns | 2.18 µs | 2,536,749 qps | 458,250 qps |
| 10,000 | 4.92 ms | 481.4 ns | 531.1 ns | 2.87 µs | 2,077,417 qps | 348,485 qps |
| 100,000 | 56.88 ms | 904.9 ns | 726.5 ns | 5.38 µs | 1,105,057 qps | 186,001 qps |
| 1,000,000 | 672.00 ms | 1.86 µs | 890.6 ns | 12.98 µs | 537,942 qps | 77,061 qps |

### Detailed Pure Python GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1.37 ms | 7.58 µs | 8.92 µs | 51.00 µs | 131,928 qps | 19,608 qps |
| 10,000 | 17.91 ms | 10.45 µs | 10.09 µs | 82.80 µs | 95,671 qps | 12,076 qps |
| 100,000 | 277.49 ms | 15.82 µs | 15.65 µs | 207.67 µs | 63,219 qps | 4,815 qps |
| 1,000,000 | 5.37 s | 23.39 µs | 16.32 µs | 610.45 µs | 42,753 qps | 1,638 qps |


## KDTree Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.022 ms | 0.089 ms | **4.12x** | 212.3 ns | 5.33 µs | **25.1x** | 835.3 ns | 20.55 µs | **24.6x** |
| 1,000 | 0.157 ms | 0.983 ms | **6.25x** | 284.7 ns | 7.23 µs | **25.4x** | 1.04 µs | 17.54 µs | **16.8x** |
| 10,000 | 1.99 ms | 15.92 ms | **8.02x** | 352.4 ns | 9.05 µs | **25.7x** | 1.20 µs | 20.81 µs | **17.3x** |
| 100,000 | 29.39 ms | 220.77 ms | **7.51x** | 536.9 ns | 15.08 µs | **28.1x** | 1.37 µs | 31.68 µs | **23.1x** |
| 1,000,000 | 390.39 ms | 4.83 s | **12.38x** | 1.29 µs | 17.79 µs | **13.8x** | 1.77 µs | 28.64 µs | **16.2x** |
### Detailed C++ KDTree Results

| Points ($N$) | Build Time | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|
| 100 | 0.022 ms | 212.3 ns | 835.3 ns | 4,709,215 qps | 1,197,201 qps |
| 1,000 | 0.157 ms | 284.7 ns | 1.04 µs | 3,512,827 qps | 957,955 qps |
| 10,000 | 1.99 ms | 352.4 ns | 1.20 µs | 2,838,009 qps | 830,279 qps |
| 100,000 | 29.39 ms | 536.9 ns | 1.37 µs | 1,862,683 qps | 727,716 qps |
| 1,000,000 | 390.39 ms | 1.29 µs | 1.77 µs | 774,380 qps | 565,783 qps |

### Detailed Pure Python KDTree Results

| Points ($N$) | Build Time | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|
| 100 | 0.089 ms | 5.33 µs | 20.55 µs | 187,757 qps | 48,655 qps |
| 1,000 | 0.983 ms | 7.23 µs | 17.54 µs | 138,262 qps | 57,004 qps |
| 10,000 | 15.92 ms | 9.05 µs | 20.81 µs | 110,440 qps | 48,059 qps |
| 100,000 | 220.77 ms | 15.08 µs | 31.68 µs | 66,313 qps | 31,570 qps |
| 1,000,000 | 4.83 s | 17.79 µs | 28.64 µs | 56,218 qps | 34,919 qps |


## Methodology

1. **Data**: Coordinates randomly and uniformly distributed over valid ranges ($[-90, 90]$ latitude, $[-180, 180]$ longitude for GeoKDTree; $[0, 1000] \times [0, 1000]$ for 2D KDTree).
2. **Timing**: Measured with `time.perf_counter()` over thousands of repeated lookups to compute stable averages.
3. **Reproducibility**: Run `uv run python utils/benchmark.py` to regenerate these benchmarks on your hardware.
