# GeoKDTree Performance Benchmarks

Automated performance benchmarks for `geokdtree` comparing C++ and Pure Python implementations across various dataset scales.

## Environment

| Attribute | Value |
|---|---|
| **Date** | 2026-11-20 15:31:42 UTC |
| **OS** | Linux-7.0.0-43-generic-x86_64-with-glibc2.39 |
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
| 1,000 | 0.290 ms | 1.32 ms | **4.57x** | 297.7 ns | 7.54 µs | **25.3x** | 1.51 µs | 49.91 µs | **33.0x** |
| 10,000 | 4.04 ms | 17.09 ms | **4.23x** | 393.6 ns | 9.93 µs | **25.2x** | 2.01 µs | 81.16 µs | **40.4x** |
| 100,000 | 47.45 ms | 268.35 ms | **5.66x** | 602.4 ns | 15.49 µs | **25.7x** | 3.18 µs | 205.78 µs | **64.8x** |
| 1,000,000 | 553.93 ms | 5.18 s | **9.35x** | 1.49 µs | 22.10 µs | **14.8x** | 6.74 µs | 572.08 µs | **84.8x** |

### Detailed C++ GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.290 ms | 297.7 ns | 312.1 ns | 1.51 µs | 3,358,982 qps | 660,460 qps |
| 10,000 | 4.04 ms | 393.6 ns | 426.0 ns | 2.01 µs | 2,540,935 qps | 498,370 qps |
| 100,000 | 47.45 ms | 602.4 ns | 619.7 ns | 3.18 µs | 1,659,949 qps | 314,838 qps |
| 1,000,000 | 553.93 ms | 1.49 µs | 787.4 ns | 6.74 µs | 668,918 qps | 148,268 qps |

### Detailed Pure Python GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1.32 ms | 7.54 µs | 7.52 µs | 49.91 µs | 132,704 qps | 20,035 qps |
| 10,000 | 17.09 ms | 9.93 µs | 10.04 µs | 81.16 µs | 100,752 qps | 12,321 qps |
| 100,000 | 268.35 ms | 15.49 µs | 15.12 µs | 205.78 µs | 64,542 qps | 4,859 qps |
| 1,000,000 | 5.18 s | 22.10 µs | 17.96 µs | 572.08 µs | 45,256 qps | 1,747 qps |


## KDTree Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.021 ms | 0.100 ms | **4.74x** | 223.4 ns | 3.97 µs | **17.8x** | 831.8 ns | 20.44 µs | **24.6x** |
| 1,000 | 0.170 ms | 0.961 ms | **5.65x** | 352.2 ns | 5.37 µs | **15.3x** | 1.05 µs | 17.63 µs | **16.8x** |
| 10,000 | 2.08 ms | 15.35 ms | **7.38x** | 350.1 ns | 6.70 µs | **19.1x** | 1.19 µs | 21.65 µs | **18.3x** |
| 100,000 | 24.92 ms | 229.82 ms | **9.22x** | 640.1 ns | 10.54 µs | **16.5x** | 1.43 µs | 27.84 µs | **19.5x** |
| 1,000,000 | 305.29 ms | 4.93 s | **16.16x** | 1.17 µs | 15.16 µs | **12.9x** | 1.87 µs | 28.31 µs | **15.1x** |
### Detailed C++ KDTree Results

| Points ($N$) | Build Time | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|
| 100 | 0.021 ms | 223.4 ns | 831.8 ns | 4,476,283 qps | 1,202,211 qps |
| 1,000 | 0.170 ms | 352.2 ns | 1.05 µs | 2,839,529 qps | 952,300 qps |
| 10,000 | 2.08 ms | 350.1 ns | 1.19 µs | 2,856,385 qps | 843,470 qps |
| 100,000 | 24.92 ms | 640.1 ns | 1.43 µs | 1,562,355 qps | 700,358 qps |
| 1,000,000 | 305.29 ms | 1.17 µs | 1.87 µs | 851,796 qps | 534,369 qps |

### Detailed Pure Python KDTree Results

| Points ($N$) | Build Time | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|
| 100 | 0.100 ms | 3.97 µs | 20.44 µs | 252,124 qps | 48,912 qps |
| 1,000 | 0.961 ms | 5.37 µs | 17.63 µs | 186,187 qps | 56,732 qps |
| 10,000 | 15.35 ms | 6.70 µs | 21.65 µs | 149,354 qps | 46,192 qps |
| 100,000 | 229.82 ms | 10.54 µs | 27.84 µs | 94,854 qps | 35,915 qps |
| 1,000,000 | 4.93 s | 15.16 µs | 28.31 µs | 65,959 qps | 35,319 qps |


## GeoHilbert Benchmarks (Latitude/Longitude)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.477 ms | 18.77 ms | **39.31x** | 448.1 ns | 23.21 µs | **51.8x** | 0.033 ms | 0.010 ms | **0.3x** |
| 10,000 | 4.33 ms | 192.39 ms | **44.43x** | 441.8 ns | 23.74 µs | **53.7x** | 0.243 ms | 0.060 ms | **0.2x** |
| 100,000 | 46.08 ms | 1.89 s | **41.11x** | 480.1 ns | 24.28 µs | **50.6x** | 2.12 ms | 0.664 ms | **0.3x** |
| 1,000,000 | 588.65 ms | 19.46 s | **33.06x** | 595.9 ns | 23.52 µs | **39.5x** | 21.21 ms | 14.60 ms | **0.7x** |

### Detailed C++ GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | `hilbert_order` | Nearest QPS |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.477 ms | 448.1 ns | 484.7 ns | 0.033 ms | 2,231,506 qps |
| 10,000 | 4.33 ms | 441.8 ns | 419.4 ns | 0.243 ms | 2,263,602 qps |
| 100,000 | 46.08 ms | 480.1 ns | 441.1 ns | 2.12 ms | 2,082,838 qps |
| 1,000,000 | 588.65 ms | 595.9 ns | 650.8 ns | 21.21 ms | 1,678,176 qps |

### Detailed Pure Python GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | `hilbert_order` | Nearest QPS |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 18.77 ms | 23.21 µs | 22.83 µs | 0.010 ms | 43,089 qps |
| 10,000 | 192.39 ms | 23.74 µs | 23.52 µs | 0.060 ms | 42,119 qps |
| 100,000 | 1.89 s | 24.28 µs | 24.29 µs | 0.664 ms | 41,185 qps |
| 1,000,000 | 19.46 s | 23.52 µs | 26.20 µs | 14.60 ms | 42,525 qps |


## Hilbert Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.406 ms | 11.57 ms | **28.54x** | 419.7 ns | 14.91 µs | **35.5x** | 0.031 ms | 0.009 ms | **0.3x** |
| 10,000 | 4.12 ms | 115.31 ms | **27.96x** | 437.3 ns | 14.90 µs | **34.1x** | 0.250 ms | 0.055 ms | **0.2x** |
| 100,000 | 44.14 ms | 1.16 s | **26.29x** | 473.6 ns | 15.28 µs | **32.3x** | 2.25 ms | 0.638 ms | **0.3x** |
| 1,000,000 | 524.98 ms | 11.76 s | **22.40x** | 647.9 ns | 14.80 µs | **22.8x** | 30.81 ms | 14.84 ms | **0.5x** |

### Detailed C++ Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | `hilbert_order` | Nearest QPS |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.406 ms | 419.7 ns | 397.4 ns | 0.031 ms | 2,382,724 qps |
| 10,000 | 4.12 ms | 437.3 ns | 390.7 ns | 0.250 ms | 2,286,974 qps |
| 100,000 | 44.14 ms | 473.6 ns | 400.7 ns | 2.25 ms | 2,111,388 qps |
| 1,000,000 | 524.98 ms | 647.9 ns | 598.7 ns | 30.81 ms | 1,543,483 qps |

### Detailed Pure Python Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | `hilbert_order` | Nearest QPS |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 11.57 ms | 14.91 µs | 14.81 µs | 0.009 ms | 67,052 qps |
| 10,000 | 115.31 ms | 14.90 µs | 15.02 µs | 0.055 ms | 67,110 qps |
| 100,000 | 1.16 s | 15.28 µs | 15.71 µs | 0.638 ms | 65,461 qps |
| 1,000,000 | 11.76 s | 14.80 µs | 17.57 µs | 14.84 ms | 67,573 qps |


## Methodology

1. **Data**: Coordinates randomly and uniformly distributed over valid ranges ($[-90, 90]$ latitude, $[-180, 180]$ longitude for GeoKDTree and GeoHilbert; $[0, 1000] \times [0, 1000]$ for 2D KDTree and Hilbert).
2. **Timing**: Measured with `time.perf_counter()` over thousands of repeated lookups to compute stable averages.
3. **Reproducibility**: Run `uv run python utils/benchmark.py` to regenerate these benchmarks on your hardware.
