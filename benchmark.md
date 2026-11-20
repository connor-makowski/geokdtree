# GeoKDTree Performance Benchmarks

Automated performance benchmarks for `geokdtree` comparing C++ and Pure Python implementations across various dataset scales.

## Environment

| Attribute | Value |
|---|---|
| **Date** | 2026-11-20 17:12:05 UTC |
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

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Batch | Python Batch | Batch Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.247 ms | 1.32 ms | **5.32x** | 275.2 ns | 7.45 µs | **27.1x** | 264.5 ns | 7.83 µs | **29.6x** | 1.52 µs | 49.03 µs | **32.2x** |
| 10,000 | 3.63 ms | 17.22 ms | **4.75x** | 373.2 ns | 10.14 µs | **27.2x** | 360.3 ns | 9.96 µs | **27.6x** | 1.92 µs | 77.42 µs | **40.3x** |
| 100,000 | 42.28 ms | 260.01 ms | **6.15x** | 567.9 ns | 14.89 µs | **26.2x** | 487.4 ns | 13.62 µs | **27.9x** | 2.93 µs | 193.88 µs | **66.1x** |
| 1,000,000 | 502.69 ms | 4.98 s | **9.90x** | 1.19 µs | 21.27 µs | **17.9x** | 663.8 ns | 13.83 µs | **20.8x** | 6.27 µs | 547.40 µs | **87.3x** |

### Detailed C++ GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | Batch (`closest_indices`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.247 ms | 275.2 ns | 305.7 ns | 264.5 ns | 1.52 µs | 3,633,380 qps | 3,780,612 qps | 657,643 qps |
| 10,000 | 3.63 ms | 373.2 ns | 402.0 ns | 360.3 ns | 1.92 µs | 2,679,742 qps | 2,775,635 qps | 521,075 qps |
| 100,000 | 42.28 ms | 567.9 ns | 584.6 ns | 487.4 ns | 2.93 µs | 1,760,777 qps | 2,051,715 qps | 340,760 qps |
| 1,000,000 | 502.69 ms | 1.19 µs | 749.5 ns | 663.8 ns | 6.27 µs | 843,593 qps | 1,506,557 qps | 159,463 qps |

### Detailed Pure Python GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | Batch (`closest_indices`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1.32 ms | 7.45 µs | 7.42 µs | 7.83 µs | 49.03 µs | 134,156 qps | 127,783 qps | 20,395 qps |
| 10,000 | 17.22 ms | 10.14 µs | 9.85 µs | 9.96 µs | 77.42 µs | 98,635 qps | 100,421 qps | 12,916 qps |
| 100,000 | 260.01 ms | 14.89 µs | 13.93 µs | 13.62 µs | 193.88 µs | 67,137 qps | 73,432 qps | 5,157 qps |
| 1,000,000 | 4.98 s | 21.27 µs | 13.93 µs | 13.83 µs | 547.40 µs | 47,008 qps | 72,317 qps | 1,826 qps |


## KDTree Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Batch | Python Batch | Batch Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.024 ms | 0.101 ms | **4.26x** | 208.3 ns | 3.99 µs | **19.1x** | 221.1 ns | 4.19 µs | **18.9x** | 835.5 ns | 20.15 µs | **24.1x** |
| 1,000 | 0.163 ms | 0.930 ms | **5.72x** | 273.4 ns | 5.22 µs | **19.1x** | 292.9 ns | 5.52 µs | **18.8x** | 1.03 µs | 17.07 µs | **16.5x** |
| 10,000 | 2.01 ms | 15.49 ms | **7.71x** | 344.8 ns | 6.70 µs | **19.4x** | 358.3 ns | 6.94 µs | **19.4x** | 1.20 µs | 20.41 µs | **17.0x** |
| 100,000 | 23.84 ms | 210.06 ms | **8.81x** | 526.0 ns | 9.49 µs | **18.0x** | 420.2 ns | 8.43 µs | **20.1x** | 1.37 µs | 24.57 µs | **18.0x** |
| 1,000,000 | 300.52 ms | 4.62 s | **15.36x** | 1.20 µs | 14.29 µs | **11.9x** | 629.0 ns | 9.39 µs | **14.9x** | 1.62 µs | 27.22 µs | **16.8x** |
### Detailed C++ KDTree Results

| Points ($N$) | Build Time | `closest_point` | Batch (`closest_points`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.024 ms | 208.3 ns | 221.1 ns | 835.5 ns | 4,800,528 qps | 4,521,842 qps | 1,196,847 qps |
| 1,000 | 0.163 ms | 273.4 ns | 292.9 ns | 1.03 µs | 3,657,960 qps | 3,414,092 qps | 968,950 qps |
| 10,000 | 2.01 ms | 344.8 ns | 358.3 ns | 1.20 µs | 2,899,910 qps | 2,791,067 qps | 835,079 qps |
| 100,000 | 23.84 ms | 526.0 ns | 420.2 ns | 1.37 µs | 1,900,992 qps | 2,379,649 qps | 731,130 qps |
| 1,000,000 | 300.52 ms | 1.20 µs | 629.0 ns | 1.62 µs | 831,504 qps | 1,589,825 qps | 616,488 qps |

### Detailed Pure Python KDTree Results

| Points ($N$) | Build Time | `closest_point` | Batch (`closest_points`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.101 ms | 3.99 µs | 4.19 µs | 20.15 µs | 250,799 qps | 238,707 qps | 49,636 qps |
| 1,000 | 0.930 ms | 5.22 µs | 5.52 µs | 17.07 µs | 191,408 qps | 181,296 qps | 58,594 qps |
| 10,000 | 15.49 ms | 6.70 µs | 6.94 µs | 20.41 µs | 149,201 qps | 144,150 qps | 49,003 qps |
| 100,000 | 210.06 ms | 9.49 µs | 8.43 µs | 24.57 µs | 105,367 qps | 118,620 qps | 40,693 qps |
| 1,000,000 | 4.62 s | 14.29 µs | 9.39 µs | 27.22 µs | 69,966 qps | 106,460 qps | 36,741 qps |


## GeoHilbert Benchmarks (Latitude/Longitude)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.457 ms | 18.65 ms | **40.82x** | 427.1 ns | 22.73 µs | **53.2x** | 0.021 ms | 0.007 ms | **0.3x** |
| 10,000 | 4.52 ms | 189.14 ms | **41.84x** | 442.8 ns | 23.03 µs | **52.0x** | 0.234 ms | 0.026 ms | **0.1x** |
| 100,000 | 47.36 ms | 1.86 s | **39.25x** | 469.3 ns | 22.71 µs | **48.4x** | 2.03 ms | 0.604 ms | **0.3x** |
| 1,000,000 | 549.80 ms | 18.95 s | **34.46x** | 636.7 ns | 23.09 µs | **36.3x** | 20.20 ms | 14.28 ms | **0.7x** |

### Detailed C++ GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.457 ms | 427.1 ns | 391.2 ns | 395.1 ns | 0.021 ms | 2,341,422 qps | 2,530,825 qps |
| 10,000 | 4.52 ms | 442.8 ns | 410.9 ns | 406.9 ns | 0.234 ms | 2,258,474 qps | 2,457,532 qps |
| 100,000 | 47.36 ms | 469.3 ns | 429.7 ns | 440.5 ns | 2.03 ms | 2,130,864 qps | 2,269,951 qps |
| 1,000,000 | 549.80 ms | 636.7 ns | 623.5 ns | 580.6 ns | 20.20 ms | 1,570,697 qps | 1,722,489 qps |

### Detailed Pure Python GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 18.65 ms | 22.73 µs | 22.77 µs | 23.04 µs | 0.007 ms | 43,987 qps | 43,395 qps |
| 10,000 | 189.14 ms | 23.03 µs | 22.92 µs | 23.23 µs | 0.026 ms | 43,418 qps | 43,055 qps |
| 100,000 | 1.86 s | 22.71 µs | 23.44 µs | 22.79 µs | 0.604 ms | 44,026 qps | 43,881 qps |
| 1,000,000 | 18.95 s | 23.09 µs | 26.09 µs | 23.19 µs | 14.28 ms | 43,308 qps | 43,121 qps |


## Hilbert Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.563 ms | 11.29 ms | **20.04x** | 419.1 ns | 14.51 µs | **34.6x** | 0.021 ms | 0.007 ms | **0.3x** |
| 10,000 | 4.10 ms | 113.75 ms | **27.76x** | 420.8 ns | 14.50 µs | **34.5x** | 0.177 ms | 0.026 ms | **0.1x** |
| 100,000 | 43.90 ms | 1.13 s | **25.76x** | 441.4 ns | 14.68 µs | **33.3x** | 2.15 ms | 0.570 ms | **0.3x** |
| 1,000,000 | 515.65 ms | 11.58 s | **22.46x** | 648.9 ns | 14.27 µs | **22.0x** | 30.48 ms | 16.64 ms | **0.5x** |

### Detailed C++ Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.563 ms | 419.1 ns | 379.5 ns | 372.7 ns | 0.021 ms | 2,386,101 qps | 2,682,810 qps |
| 10,000 | 4.10 ms | 420.8 ns | 374.1 ns | 393.6 ns | 0.177 ms | 2,376,703 qps | 2,540,436 qps |
| 100,000 | 43.90 ms | 441.4 ns | 411.4 ns | 419.7 ns | 2.15 ms | 2,265,262 qps | 2,382,722 qps |
| 1,000,000 | 515.65 ms | 648.9 ns | 594.3 ns | 500.6 ns | 30.48 ms | 1,541,105 qps | 1,997,782 qps |

### Detailed Pure Python Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 11.29 ms | 14.51 µs | 14.53 µs | 14.72 µs | 0.007 ms | 68,935 qps | 67,937 qps |
| 10,000 | 113.75 ms | 14.50 µs | 14.43 µs | 14.51 µs | 0.026 ms | 68,961 qps | 68,939 qps |
| 100,000 | 1.13 s | 14.68 µs | 15.14 µs | 14.83 µs | 0.570 ms | 68,114 qps | 67,452 qps |
| 1,000,000 | 11.58 s | 14.27 µs | 17.39 µs | 14.69 µs | 16.64 ms | 70,086 qps | 68,067 qps |


## Methodology

1. **Data**: Coordinates randomly and uniformly distributed over valid ranges ($[-90, 90]$ latitude, $[-180, 180]$ longitude for GeoKDTree and GeoHilbert; $[0, 1000] \times [0, 1000]$ for 2D KDTree and Hilbert).
2. **Timing**: Measured with `time.perf_counter()` over thousands of repeated lookups to compute stable averages.
3. **Reproducibility**: Run `uv run python utils/benchmark.py` to regenerate these benchmarks on your hardware.
