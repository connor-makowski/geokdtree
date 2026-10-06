# GeoKDTree Performance Benchmarks

Automated performance benchmarks for `geokdtree` comparing C++ and Pure Python implementations across various dataset scales.

## Environment

| Attribute | Value |
|---|---|
| **Date** | 2026-10-06 19:17:01 UTC |
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
| 1,000 | 0.415 ms | 1.37 ms | **3.30x** | 406.2 ns | 7.73 µs | **19.0x** | 2.18 µs | 50.92 µs | **23.3x** |
| 10,000 | 4.85 ms | 17.79 ms | **3.67x** | 494.2 ns | 9.89 µs | **20.0x** | 2.88 µs | 79.38 µs | **27.6x** |
| 100,000 | 56.97 ms | 266.48 ms | **4.68x** | 883.4 ns | 15.40 µs | **17.4x** | 5.50 µs | 201.93 µs | **36.7x** |
| 1,000,000 | 668.74 ms | 5.41 s | **8.09x** | 1.78 µs | 22.39 µs | **12.6x** | 12.75 µs | 582.50 µs | **45.7x** |

### Detailed C++ GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.415 ms | 406.2 ns | 405.6 ns | 2.18 µs | 2,462,048 qps | 457,807 qps |
| 10,000 | 4.85 ms | 494.2 ns | 501.0 ns | 2.88 µs | 2,023,567 qps | 347,534 qps |
| 100,000 | 56.97 ms | 883.4 ns | 741.0 ns | 5.50 µs | 1,132,047 qps | 181,822 qps |
| 1,000,000 | 668.74 ms | 1.78 µs | 903.1 ns | 12.75 µs | 561,490 qps | 78,448 qps |

### Detailed Pure Python GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1.37 ms | 7.73 µs | 7.66 µs | 50.92 µs | 129,315 qps | 19,636 qps |
| 10,000 | 17.79 ms | 9.89 µs | 9.94 µs | 79.38 µs | 101,116 qps | 12,596 qps |
| 100,000 | 266.48 ms | 15.40 µs | 14.28 µs | 201.93 µs | 64,921 qps | 4,952 qps |
| 1,000,000 | 5.41 s | 22.39 µs | 20.97 µs | 582.50 µs | 44,664 qps | 1,716 qps |


## KDTree Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.020 ms | 0.124 ms | **6.13x** | 213.9 ns | 5.44 µs | **25.4x** | 845.5 ns | 20.17 µs | **23.9x** |
| 1,000 | 0.164 ms | 1.01 ms | **6.17x** | 298.1 ns | 7.37 µs | **24.7x** | 1.07 µs | 17.80 µs | **16.7x** |
| 10,000 | 2.01 ms | 16.53 ms | **8.23x** | 359.3 ns | 9.23 µs | **25.7x** | 1.22 µs | 21.14 µs | **17.4x** |
| 100,000 | 28.75 ms | 229.88 ms | **8.00x** | 560.3 ns | 13.11 µs | **23.4x** | 1.41 µs | 32.32 µs | **23.0x** |
| 1,000,000 | 392.56 ms | 5.20 s | **13.25x** | 1.29 µs | 20.26 µs | **15.7x** | 1.88 µs | 34.63 µs | **18.4x** |
### Detailed C++ KDTree Results

| Points ($N$) | Build Time | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|
| 100 | 0.020 ms | 213.9 ns | 845.5 ns | 4,675,094 qps | 1,182,747 qps |
| 1,000 | 0.164 ms | 298.1 ns | 1.07 µs | 3,354,340 qps | 937,384 qps |
| 10,000 | 2.01 ms | 359.3 ns | 1.22 µs | 2,783,352 qps | 821,274 qps |
| 100,000 | 28.75 ms | 560.3 ns | 1.41 µs | 1,784,624 qps | 711,742 qps |
| 1,000,000 | 392.56 ms | 1.29 µs | 1.88 µs | 776,795 qps | 532,450 qps |

### Detailed Pure Python KDTree Results

| Points ($N$) | Build Time | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|
| 100 | 0.124 ms | 5.44 µs | 20.17 µs | 183,747 qps | 49,574 qps |
| 1,000 | 1.01 ms | 7.37 µs | 17.80 µs | 135,750 qps | 56,165 qps |
| 10,000 | 16.53 ms | 9.23 µs | 21.14 µs | 108,347 qps | 47,307 qps |
| 100,000 | 229.88 ms | 13.11 µs | 32.32 µs | 76,263 qps | 30,939 qps |
| 1,000,000 | 5.20 s | 20.26 µs | 34.63 µs | 49,361 qps | 28,878 qps |


## Methodology

1. **Data**: Coordinates randomly and uniformly distributed over valid ranges ($[-90, 90]$ latitude, $[-180, 180]$ longitude for GeoKDTree; $[0, 1000] \times [0, 1000]$ for 2D KDTree).
2. **Timing**: Measured with `time.perf_counter()` over thousands of repeated lookups to compute stable averages.
3. **Reproducibility**: Run `uv run python utils/benchmark.py` to regenerate these benchmarks on your hardware.
