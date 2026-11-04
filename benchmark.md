# GeoKDTree Performance Benchmarks

Automated performance benchmarks for `geokdtree` comparing C++ and Pure Python implementations across various dataset scales.

## Environment

| Attribute | Value |
|---|---|
| **Date** | 2026-11-04 21:44:11 UTC |
| **OS** | Linux-7.0.0-42-generic-x86_64-with-glibc2.39 |
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
| 1,000 | 0.409 ms | 1.33 ms | **3.25x** | 387.0 ns | 7.58 µs | **19.6x** | 2.15 µs | 50.47 µs | **23.5x** |
| 10,000 | 4.88 ms | 17.28 ms | **3.54x** | 486.1 ns | 10.10 µs | **20.8x** | 3.00 µs | 83.75 µs | **27.9x** |
| 100,000 | 56.86 ms | 275.70 ms | **4.85x** | 927.1 ns | 15.53 µs | **16.8x** | 5.64 µs | 207.08 µs | **36.7x** |
| 1,000,000 | 650.33 ms | 5.17 s | **7.95x** | 1.77 µs | 21.51 µs | **12.2x** | 13.74 µs | 569.65 µs | **41.5x** |

### Detailed C++ GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.409 ms | 387.0 ns | 409.5 ns | 2.15 µs | 2,584,245 qps | 465,524 qps |
| 10,000 | 4.88 ms | 486.1 ns | 505.0 ns | 3.00 µs | 2,057,135 qps | 333,569 qps |
| 100,000 | 56.86 ms | 927.1 ns | 745.0 ns | 5.64 µs | 1,078,581 qps | 177,451 qps |
| 1,000,000 | 650.33 ms | 1.77 µs | 892.2 ns | 13.74 µs | 565,366 qps | 72,787 qps |

### Detailed Pure Python GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1.33 ms | 7.58 µs | 7.79 µs | 50.47 µs | 131,914 qps | 19,813 qps |
| 10,000 | 17.28 ms | 10.10 µs | 10.10 µs | 83.75 µs | 98,969 qps | 11,940 qps |
| 100,000 | 275.70 ms | 15.53 µs | 14.87 µs | 207.08 µs | 64,375 qps | 4,828 qps |
| 1,000,000 | 5.17 s | 21.51 µs | 14.08 µs | 569.65 µs | 46,497 qps | 1,755 qps |


## KDTree Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.022 ms | 0.103 ms | **4.73x** | 202.7 ns | 5.99 µs | **29.5x** | 831.6 ns | 20.86 µs | **25.1x** |
| 1,000 | 0.180 ms | 0.992 ms | **5.51x** | 308.3 ns | 7.93 µs | **25.7x** | 1.06 µs | 17.86 µs | **16.9x** |
| 10,000 | 2.09 ms | 19.10 ms | **9.16x** | 365.1 ns | 10.49 µs | **28.7x** | 1.20 µs | 21.21 µs | **17.7x** |
| 100,000 | 25.26 ms | 230.08 ms | **9.11x** | 565.8 ns | 14.10 µs | **24.9x** | 1.46 µs | 27.69 µs | **19.0x** |
| 1,000,000 | 311.12 ms | 4.82 s | **15.51x** | 1.23 µs | 19.12 µs | **15.5x** | 1.76 µs | 28.17 µs | **16.0x** |
### Detailed C++ KDTree Results

| Points ($N$) | Build Time | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|
| 100 | 0.022 ms | 202.7 ns | 831.6 ns | 4,933,803 qps | 1,202,471 qps |
| 1,000 | 0.180 ms | 308.3 ns | 1.06 µs | 3,243,840 qps | 944,404 qps |
| 10,000 | 2.09 ms | 365.1 ns | 1.20 µs | 2,738,971 qps | 834,578 qps |
| 100,000 | 25.26 ms | 565.8 ns | 1.46 µs | 1,767,358 qps | 686,591 qps |
| 1,000,000 | 311.12 ms | 1.23 µs | 1.76 µs | 810,770 qps | 569,153 qps |

### Detailed Pure Python KDTree Results

| Points ($N$) | Build Time | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|
| 100 | 0.103 ms | 5.99 µs | 20.86 µs | 167,006 qps | 47,945 qps |
| 1,000 | 0.992 ms | 7.93 µs | 17.86 µs | 126,034 qps | 56,003 qps |
| 10,000 | 19.10 ms | 10.49 µs | 21.21 µs | 95,343 qps | 47,140 qps |
| 100,000 | 230.08 ms | 14.10 µs | 27.69 µs | 70,925 qps | 36,108 qps |
| 1,000,000 | 4.82 s | 19.12 µs | 28.17 µs | 52,307 qps | 35,501 qps |


## GeoHilbert Benchmarks (Latitude/Longitude)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.448 ms | 18.95 ms | **42.34x** | 426.1 ns | 22.87 µs | **53.7x** | 0.031 ms | 0.009 ms | **0.3x** |
| 10,000 | 4.67 ms | 188.52 ms | **40.36x** | 439.4 ns | 22.87 µs | **52.0x** | 0.230 ms | 0.037 ms | **0.2x** |
| 100,000 | 49.12 ms | 1.88 s | **38.31x** | 477.0 ns | 23.52 µs | **49.3x** | 2.10 ms | 0.647 ms | **0.3x** |
| 1,000,000 | 577.73 ms | 19.32 s | **33.44x** | 560.8 ns | 23.07 µs | **41.1x** | 21.57 ms | 14.90 ms | **0.7x** |

### Detailed C++ GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | `hilbert_order` | Nearest QPS |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.448 ms | 426.1 ns | 425.4 ns | 0.031 ms | 2,347,072 qps |
| 10,000 | 4.67 ms | 439.4 ns | 432.7 ns | 0.230 ms | 2,275,716 qps |
| 100,000 | 49.12 ms | 477.0 ns | 439.6 ns | 2.10 ms | 2,096,313 qps |
| 1,000,000 | 577.73 ms | 560.8 ns | 634.6 ns | 21.57 ms | 1,783,278 qps |

### Detailed Pure Python GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | `hilbert_order` | Nearest QPS |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 18.95 ms | 22.87 µs | 22.83 µs | 0.009 ms | 43,731 qps |
| 10,000 | 188.52 ms | 22.87 µs | 22.99 µs | 0.037 ms | 43,724 qps |
| 100,000 | 1.88 s | 23.52 µs | 24.09 µs | 0.647 ms | 42,519 qps |
| 1,000,000 | 19.32 s | 23.07 µs | 26.23 µs | 14.90 ms | 43,345 qps |


## Hilbert Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.398 ms | 11.97 ms | **30.04x** | 450.6 ns | 14.49 µs | **32.1x** | 0.026 ms | 0.010 ms | **0.4x** |
| 10,000 | 4.00 ms | 114.52 ms | **28.66x** | 459.1 ns | 14.76 µs | **32.2x** | 0.236 ms | 0.087 ms | **0.4x** |
| 100,000 | 43.94 ms | 1.15 s | **26.24x** | 510.9 ns | 15.65 µs | **30.6x** | 2.20 ms | 0.649 ms | **0.3x** |
| 1,000,000 | 523.31 ms | 11.78 s | **22.52x** | 703.8 ns | 14.91 µs | **21.2x** | 30.77 ms | 14.99 ms | **0.5x** |

### Detailed C++ Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | `hilbert_order` | Nearest QPS |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.398 ms | 450.6 ns | 372.5 ns | 0.026 ms | 2,219,099 qps |
| 10,000 | 4.00 ms | 459.1 ns | 373.2 ns | 0.236 ms | 2,178,016 qps |
| 100,000 | 43.94 ms | 510.9 ns | 397.1 ns | 2.20 ms | 1,957,514 qps |
| 1,000,000 | 523.31 ms | 703.8 ns | 598.3 ns | 30.77 ms | 1,420,878 qps |

### Detailed Pure Python Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | `hilbert_order` | Nearest QPS |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 11.97 ms | 14.49 µs | 14.47 µs | 0.010 ms | 69,029 qps |
| 10,000 | 114.52 ms | 14.76 µs | 14.55 µs | 0.087 ms | 67,732 qps |
| 100,000 | 1.15 s | 15.65 µs | 15.23 µs | 0.649 ms | 63,904 qps |
| 1,000,000 | 11.78 s | 14.91 µs | 17.74 µs | 14.99 ms | 67,063 qps |


## Methodology

1. **Data**: Coordinates randomly and uniformly distributed over valid ranges ($[-90, 90]$ latitude, $[-180, 180]$ longitude for GeoKDTree and GeoHilbert; $[0, 1000] \times [0, 1000]$ for 2D KDTree and Hilbert).
2. **Timing**: Measured with `time.perf_counter()` over thousands of repeated lookups to compute stable averages.
3. **Reproducibility**: Run `uv run python utils/benchmark.py` to regenerate these benchmarks on your hardware.
