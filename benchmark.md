# GeoKDTree Performance Benchmarks

Automated performance benchmarks for `geokdtree` comparing C++ and Pure Python implementations across various dataset scales.

## Environment

| Attribute | Value |
|---|---|
| **Date** | 2026-11-23 14:01:38 UTC |
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
| 1,000 | 0.127 ms | 1.34 ms | **10.50x** | 273.1 ns | 7.54 µs | **27.6x** | 260.5 ns | 7.76 µs | **29.8x** | 1.47 µs | 49.50 µs | **33.7x** |
| 10,000 | 2.09 ms | 17.08 ms | **8.18x** | 369.7 ns | 9.75 µs | **26.4x** | 334.9 ns | 10.00 µs | **29.8x** | 1.82 µs | 78.23 µs | **42.9x** |
| 100,000 | 23.22 ms | 264.95 ms | **11.41x** | 525.8 ns | 15.19 µs | **28.9x** | 450.3 ns | 14.41 µs | **32.0x** | 2.67 µs | 198.11 µs | **74.1x** |
| 1,000,000 | 285.32 ms | 5.12 s | **17.95x** | 1.35 µs | 21.22 µs | **15.7x** | 642.6 ns | 14.15 µs | **22.0x** | 5.99 µs | 556.12 µs | **92.9x** |

### Detailed C++ GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | Batch (`closest_indices`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.127 ms | 273.1 ns | 297.4 ns | 260.5 ns | 1.47 µs | 3,661,839 qps | 3,838,756 qps | 681,213 qps |
| 10,000 | 2.09 ms | 369.7 ns | 392.7 ns | 334.9 ns | 1.82 µs | 2,704,989 qps | 2,985,653 qps | 548,000 qps |
| 100,000 | 23.22 ms | 525.8 ns | 484.8 ns | 450.3 ns | 2.67 µs | 1,901,925 qps | 2,220,598 qps | 374,129 qps |
| 1,000,000 | 285.32 ms | 1.35 µs | 651.9 ns | 642.6 ns | 5.99 µs | 741,001 qps | 1,556,238 qps | 167,021 qps |

### Detailed Pure Python GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | Batch (`closest_indices`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1.34 ms | 7.54 µs | 7.63 µs | 7.76 µs | 49.50 µs | 132,549 qps | 128,907 qps | 20,202 qps |
| 10,000 | 17.08 ms | 9.75 µs | 9.85 µs | 10.00 µs | 78.23 µs | 102,588 qps | 100,040 qps | 12,782 qps |
| 100,000 | 264.95 ms | 15.19 µs | 14.56 µs | 14.41 µs | 198.11 µs | 65,821 qps | 69,383 qps | 5,047 qps |
| 1,000,000 | 5.12 s | 21.22 µs | 14.47 µs | 14.15 µs | 556.12 µs | 47,118 qps | 70,679 qps | 1,798 qps |


## KDTree Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Batch | Python Batch | Batch Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.023 ms | 0.121 ms | **5.33x** | 211.1 ns | 4.03 µs | **19.1x** | 232.8 ns | 4.25 µs | **18.3x** | 846.1 ns | 19.94 µs | **23.6x** |
| 1,000 | 0.156 ms | 0.955 ms | **6.13x** | 272.1 ns | 5.31 µs | **19.5x** | 305.9 ns | 5.55 µs | **18.2x** | 1.05 µs | 17.42 µs | **16.5x** |
| 10,000 | 1.78 ms | 15.50 ms | **8.69x** | 336.8 ns | 6.70 µs | **19.9x** | 366.4 ns | 7.01 µs | **19.1x** | 1.18 µs | 20.87 µs | **17.7x** |
| 100,000 | 22.38 ms | 229.68 ms | **10.26x** | 570.1 ns | 9.92 µs | **17.4x** | 437.6 ns | 9.77 µs | **22.3x** | 1.41 µs | 28.01 µs | **19.8x** |
| 1,000,000 | 263.06 ms | 4.96 s | **18.85x** | 1.16 µs | 15.02 µs | **12.9x** | 643.6 ns | 9.62 µs | **15.0x** | 1.77 µs | 27.95 µs | **15.8x** |
### Detailed C++ KDTree Results

| Points ($N$) | Build Time | `closest_point` | Batch (`closest_points`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.023 ms | 211.1 ns | 232.8 ns | 846.1 ns | 4,736,898 qps | 4,295,606 qps | 1,181,908 qps |
| 1,000 | 0.156 ms | 272.1 ns | 305.9 ns | 1.05 µs | 3,675,241 qps | 3,268,599 qps | 949,776 qps |
| 10,000 | 1.78 ms | 336.8 ns | 366.4 ns | 1.18 µs | 2,969,084 qps | 2,729,504 qps | 848,722 qps |
| 100,000 | 22.38 ms | 570.1 ns | 437.6 ns | 1.41 µs | 1,754,087 qps | 2,284,956 qps | 708,616 qps |
| 1,000,000 | 263.06 ms | 1.16 µs | 643.6 ns | 1.77 µs | 859,945 qps | 1,553,820 qps | 563,575 qps |

### Detailed Pure Python KDTree Results

| Points ($N$) | Build Time | `closest_point` | Batch (`closest_points`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.121 ms | 4.03 µs | 4.25 µs | 19.94 µs | 248,088 qps | 235,224 qps | 50,142 qps |
| 1,000 | 0.955 ms | 5.31 µs | 5.55 µs | 17.42 µs | 188,298 qps | 180,043 qps | 57,399 qps |
| 10,000 | 15.50 ms | 6.70 µs | 7.01 µs | 20.87 µs | 149,205 qps | 142,719 qps | 47,916 qps |
| 100,000 | 229.68 ms | 9.92 µs | 9.77 µs | 28.01 µs | 100,825 qps | 102,359 qps | 35,701 qps |
| 1,000,000 | 4.96 s | 15.02 µs | 9.62 µs | 27.95 µs | 66,590 qps | 103,915 qps | 35,771 qps |


## GeoHilbert Benchmarks (Latitude/Longitude)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.440 ms | 18.66 ms | **42.44x** | 432.6 ns | 22.75 µs | **52.6x** | 0.023 ms | 0.008 ms | **0.3x** |
| 10,000 | 4.00 ms | 187.10 ms | **46.76x** | 448.5 ns | 23.24 µs | **51.8x** | 0.198 ms | 0.033 ms | **0.2x** |
| 100,000 | 41.28 ms | 1.88 s | **45.51x** | 551.1 ns | 23.97 µs | **43.5x** | 2.19 ms | 0.626 ms | **0.3x** |
| 1,000,000 | 474.44 ms | 19.53 s | **41.16x** | 675.9 ns | 24.81 µs | **36.7x** | 21.10 ms | 15.12 ms | **0.7x** |

### Detailed C++ GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.440 ms | 432.6 ns | 413.9 ns | 374.6 ns | 0.023 ms | 2,311,718 qps | 2,669,184 qps |
| 10,000 | 4.00 ms | 448.5 ns | 427.5 ns | 393.2 ns | 0.198 ms | 2,229,619 qps | 2,543,108 qps |
| 100,000 | 41.28 ms | 551.1 ns | 440.7 ns | 438.0 ns | 2.19 ms | 1,814,552 qps | 2,283,078 qps |
| 1,000,000 | 474.44 ms | 675.9 ns | 670.1 ns | 583.6 ns | 21.10 ms | 1,479,432 qps | 1,713,473 qps |

### Detailed Pure Python GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 18.66 ms | 22.75 µs | 22.72 µs | 23.09 µs | 0.008 ms | 43,949 qps | 43,306 qps |
| 10,000 | 187.10 ms | 23.24 µs | 23.14 µs | 23.21 µs | 0.033 ms | 43,025 qps | 43,085 qps |
| 100,000 | 1.88 s | 23.97 µs | 24.30 µs | 24.19 µs | 0.626 ms | 41,725 qps | 41,334 qps |
| 1,000,000 | 19.53 s | 24.81 µs | 27.74 µs | 23.78 µs | 15.12 ms | 40,307 qps | 42,057 qps |


## Hilbert Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.388 ms | 11.72 ms | **30.23x** | 413.9 ns | 14.83 µs | **35.8x** | 0.023 ms | 0.008 ms | **0.3x** |
| 10,000 | 3.77 ms | 116.31 ms | **30.87x** | 452.3 ns | 15.32 µs | **33.9x** | 0.191 ms | 0.071 ms | **0.4x** |
| 100,000 | 40.68 ms | 1.16 s | **28.63x** | 450.3 ns | 15.65 µs | **34.8x** | 2.11 ms | 0.635 ms | **0.3x** |
| 1,000,000 | 469.58 ms | 11.86 s | **25.25x** | 674.8 ns | 14.76 µs | **21.9x** | 28.13 ms | 14.61 ms | **0.5x** |

### Detailed C++ Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.388 ms | 413.9 ns | 375.8 ns | 367.8 ns | 0.023 ms | 2,415,818 qps | 2,719,115 qps |
| 10,000 | 3.77 ms | 452.3 ns | 372.5 ns | 403.9 ns | 0.191 ms | 2,210,884 qps | 2,475,974 qps |
| 100,000 | 40.68 ms | 450.3 ns | 394.7 ns | 406.8 ns | 2.11 ms | 2,220,948 qps | 2,458,059 qps |
| 1,000,000 | 469.58 ms | 674.8 ns | 628.7 ns | 491.1 ns | 28.13 ms | 1,481,953 qps | 2,036,100 qps |

### Detailed Pure Python Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 11.72 ms | 14.83 µs | 14.82 µs | 14.88 µs | 0.008 ms | 67,438 qps | 67,188 qps |
| 10,000 | 116.31 ms | 15.32 µs | 15.66 µs | 15.14 µs | 0.071 ms | 65,289 qps | 66,061 qps |
| 100,000 | 1.16 s | 15.65 µs | 15.35 µs | 15.88 µs | 0.635 ms | 63,903 qps | 62,966 qps |
| 1,000,000 | 11.86 s | 14.76 µs | 17.64 µs | 15.49 µs | 14.61 ms | 67,768 qps | 64,543 qps |


## Methodology

1. **Data**: Coordinates randomly and uniformly distributed over valid ranges ($[-90, 90]$ latitude, $[-180, 180]$ longitude for GeoKDTree and GeoHilbert; $[0, 1000] \times [0, 1000]$ for 2D KDTree and Hilbert).
2. **Timing**: Measured with `time.perf_counter()` over thousands of repeated lookups to compute stable averages.
3. **Reproducibility**: Run `uv run python utils/benchmark.py` to regenerate these benchmarks on your hardware.
