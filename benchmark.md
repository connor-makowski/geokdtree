# GeoKDTree Performance Benchmarks

Automated performance benchmarks for `geokdtree` comparing C++ and Pure Python implementations across various dataset scales.

## Environment

| Attribute | Value |
|---|---|
| **Date** | 2026-11-20 20:27:25 UTC |
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
| 1,000 | 0.220 ms | 1.33 ms | **6.05x** | 281.1 ns | 7.70 µs | **27.4x** | 291.5 ns | 8.40 µs | **28.8x** | 1.49 µs | 51.09 µs | **34.3x** |
| 10,000 | 3.49 ms | 18.59 ms | **5.33x** | 357.1 ns | 10.08 µs | **28.2x** | 339.1 ns | 10.24 µs | **30.2x** | 1.89 µs | 81.56 µs | **43.1x** |
| 100,000 | 40.33 ms | 274.52 ms | **6.81x** | 590.9 ns | 15.91 µs | **26.9x** | 477.9 ns | 15.80 µs | **33.1x** | 3.09 µs | 213.26 µs | **69.1x** |
| 1,000,000 | 472.34 ms | 5.29 s | **11.19x** | 1.32 µs | 21.82 µs | **16.5x** | 642.2 ns | 14.11 µs | **22.0x** | 6.18 µs | 574.43 µs | **93.0x** |

### Detailed C++ GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | Batch (`closest_indices`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.220 ms | 281.1 ns | 382.0 ns | 291.5 ns | 1.49 µs | 3,557,139 qps | 3,430,289 qps | 670,684 qps |
| 10,000 | 3.49 ms | 357.1 ns | 390.7 ns | 339.1 ns | 1.89 µs | 2,800,088 qps | 2,949,093 qps | 528,771 qps |
| 100,000 | 40.33 ms | 590.9 ns | 578.6 ns | 477.9 ns | 3.09 µs | 1,692,204 qps | 2,092,663 qps | 323,953 qps |
| 1,000,000 | 472.34 ms | 1.32 µs | 734.1 ns | 642.2 ns | 6.18 µs | 757,082 qps | 1,557,220 qps | 161,842 qps |

### Detailed Pure Python GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | Batch (`closest_indices`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1.33 ms | 7.70 µs | 7.69 µs | 8.40 µs | 51.09 µs | 129,852 qps | 119,009 qps | 19,573 qps |
| 10,000 | 18.59 ms | 10.08 µs | 10.06 µs | 10.24 µs | 81.56 µs | 99,249 qps | 97,686 qps | 12,261 qps |
| 100,000 | 274.52 ms | 15.91 µs | 15.35 µs | 15.80 µs | 213.26 µs | 62,835 qps | 63,306 qps | 4,689 qps |
| 1,000,000 | 5.29 s | 21.82 µs | 14.65 µs | 14.11 µs | 574.43 µs | 45,837 qps | 70,890 qps | 1,740 qps |


## KDTree Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Batch | Python Batch | Batch Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.020 ms | 0.097 ms | **4.94x** | 227.2 ns | 4.06 µs | **17.9x** | 235.7 ns | 4.27 µs | **18.1x** | 880.5 ns | 20.39 µs | **23.2x** |
| 1,000 | 0.150 ms | 0.962 ms | **6.40x** | 293.2 ns | 5.39 µs | **18.4x** | 329.6 ns | 5.67 µs | **17.2x** | 1.09 µs | 17.59 µs | **16.2x** |
| 10,000 | 1.80 ms | 15.68 ms | **8.73x** | 362.0 ns | 6.82 µs | **18.8x** | 377.7 ns | 7.15 µs | **18.9x** | 1.24 µs | 20.96 µs | **16.9x** |
| 100,000 | 21.21 ms | 223.60 ms | **10.54x** | 574.5 ns | 9.81 µs | **17.1x** | 426.8 ns | 10.42 µs | **24.4x** | 1.43 µs | 28.33 µs | **19.8x** |
| 1,000,000 | 270.85 ms | 4.91 s | **18.13x** | 1.30 µs | 14.86 µs | **11.5x** | 700.0 ns | 9.66 µs | **13.8x** | 1.81 µs | 28.39 µs | **15.7x** |
### Detailed C++ KDTree Results

| Points ($N$) | Build Time | `closest_point` | Batch (`closest_points`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.020 ms | 227.2 ns | 235.7 ns | 880.5 ns | 4,401,675 qps | 4,243,142 qps | 1,135,732 qps |
| 1,000 | 0.150 ms | 293.2 ns | 329.6 ns | 1.09 µs | 3,410,269 qps | 3,033,693 qps | 918,329 qps |
| 10,000 | 1.80 ms | 362.0 ns | 377.7 ns | 1.24 µs | 2,762,638 qps | 2,647,908 qps | 807,774 qps |
| 100,000 | 21.21 ms | 574.5 ns | 426.8 ns | 1.43 µs | 1,740,513 qps | 2,342,836 qps | 700,522 qps |
| 1,000,000 | 270.85 ms | 1.30 µs | 700.0 ns | 1.81 µs | 771,146 qps | 1,428,602 qps | 551,450 qps |

### Detailed Pure Python KDTree Results

| Points ($N$) | Build Time | `closest_point` | Batch (`closest_points`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.097 ms | 4.06 µs | 4.27 µs | 20.39 µs | 246,573 qps | 234,435 qps | 49,034 qps |
| 1,000 | 0.962 ms | 5.39 µs | 5.67 µs | 17.59 µs | 185,436 qps | 176,459 qps | 56,862 qps |
| 10,000 | 15.68 ms | 6.82 µs | 7.15 µs | 20.96 µs | 146,601 qps | 139,820 qps | 47,699 qps |
| 100,000 | 223.60 ms | 9.81 µs | 10.42 µs | 28.33 µs | 101,899 qps | 95,967 qps | 35,301 qps |
| 1,000,000 | 4.91 s | 14.86 µs | 9.66 µs | 28.39 µs | 67,309 qps | 103,544 qps | 35,220 qps |


## GeoHilbert Benchmarks (Latitude/Longitude)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.481 ms | 18.93 ms | **39.33x** | 449.9 ns | 23.67 µs | **52.6x** | 0.028 ms | 0.008 ms | **0.3x** |
| 10,000 | 4.58 ms | 191.65 ms | **41.85x** | 451.3 ns | 23.53 µs | **52.1x** | 0.181 ms | 0.035 ms | **0.2x** |
| 100,000 | 47.89 ms | 1.91 s | **39.83x** | 484.1 ns | 23.38 µs | **48.3x** | 2.19 ms | 1.03 ms | **0.5x** |
| 1,000,000 | 582.84 ms | 19.44 s | **33.36x** | 573.4 ns | 23.94 µs | **41.8x** | 22.39 ms | 14.94 ms | **0.7x** |

### Detailed C++ GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.481 ms | 449.9 ns | 420.8 ns | 395.9 ns | 0.028 ms | 2,222,655 qps | 2,525,728 qps |
| 10,000 | 4.58 ms | 451.3 ns | 424.3 ns | 396.6 ns | 0.181 ms | 2,215,906 qps | 2,521,287 qps |
| 100,000 | 47.89 ms | 484.1 ns | 437.7 ns | 447.4 ns | 2.19 ms | 2,065,641 qps | 2,235,131 qps |
| 1,000,000 | 582.84 ms | 573.4 ns | 655.2 ns | 1.46 µs | 22.39 ms | 1,744,013 qps | 687,110 qps |

### Detailed Pure Python GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 18.93 ms | 23.67 µs | 23.42 µs | 23.35 µs | 0.008 ms | 42,255 qps | 42,824 qps |
| 10,000 | 191.65 ms | 23.53 µs | 23.42 µs | 24.02 µs | 0.035 ms | 42,495 qps | 41,627 qps |
| 100,000 | 1.91 s | 23.38 µs | 24.64 µs | 24.86 µs | 1.03 ms | 42,772 qps | 40,225 qps |
| 1,000,000 | 19.44 s | 23.94 µs | 27.63 µs | 23.36 µs | 14.94 ms | 41,771 qps | 42,811 qps |


## Hilbert Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.426 ms | 11.54 ms | **27.10x** | 411.2 ns | 14.43 µs | **35.1x** | 0.023 ms | 0.008 ms | **0.4x** |
| 10,000 | 4.04 ms | 115.78 ms | **28.64x** | 430.5 ns | 14.73 µs | **34.2x** | 0.172 ms | 0.047 ms | **0.3x** |
| 100,000 | 42.98 ms | 1.16 s | **27.01x** | 436.3 ns | 15.01 µs | **34.4x** | 2.38 ms | 0.610 ms | **0.3x** |
| 1,000,000 | 532.27 ms | 11.87 s | **22.30x** | 671.7 ns | 16.55 µs | **24.6x** | 32.98 ms | 17.72 ms | **0.5x** |

### Detailed C++ Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.426 ms | 411.2 ns | 365.2 ns | 385.9 ns | 0.023 ms | 2,431,749 qps | 2,591,207 qps |
| 10,000 | 4.04 ms | 430.5 ns | 378.7 ns | 402.1 ns | 0.172 ms | 2,322,809 qps | 2,486,887 qps |
| 100,000 | 42.98 ms | 436.3 ns | 415.7 ns | 414.7 ns | 2.38 ms | 2,292,053 qps | 2,411,213 qps |
| 1,000,000 | 532.27 ms | 671.7 ns | 610.2 ns | 515.3 ns | 32.98 ms | 1,488,815 qps | 1,940,504 qps |

### Detailed Pure Python Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 11.54 ms | 14.43 µs | 14.54 µs | 14.70 µs | 0.008 ms | 69,276 qps | 68,033 qps |
| 10,000 | 115.78 ms | 14.73 µs | 14.72 µs | 14.93 µs | 0.047 ms | 67,906 qps | 66,994 qps |
| 100,000 | 1.16 s | 15.01 µs | 15.34 µs | 14.75 µs | 0.610 ms | 66,629 qps | 67,791 qps |
| 1,000,000 | 11.87 s | 16.55 µs | 17.84 µs | 16.60 µs | 17.72 ms | 60,420 qps | 60,239 qps |


## Methodology

1. **Data**: Coordinates randomly and uniformly distributed over valid ranges ($[-90, 90]$ latitude, $[-180, 180]$ longitude for GeoKDTree and GeoHilbert; $[0, 1000] \times [0, 1000]$ for 2D KDTree and Hilbert).
2. **Timing**: Measured with `time.perf_counter()` over thousands of repeated lookups to compute stable averages.
3. **Reproducibility**: Run `uv run python utils/benchmark.py` to regenerate these benchmarks on your hardware.
