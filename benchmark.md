# GeoKDTree Performance Benchmarks

Automated performance benchmarks for `geokdtree` comparing C++ and Pure Python implementations across various dataset scales.

## Environment

| Attribute | Value |
|---|---|
| **Date** | 2026-11-20 20:17:46 UTC |
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
| 1,000 | 0.254 ms | 1.32 ms | **5.19x** | 265.8 ns | 7.51 µs | **28.2x** | 265.5 ns | 7.86 µs | **29.6x** | 1.52 µs | 49.60 µs | **32.7x** |
| 10,000 | 3.71 ms | 17.15 ms | **4.62x** | 360.4 ns | 9.75 µs | **27.1x** | 349.5 ns | 10.09 µs | **28.9x** | 1.91 µs | 78.00 µs | **40.8x** |
| 100,000 | 42.75 ms | 256.88 ms | **6.01x** | 526.2 ns | 14.94 µs | **28.4x** | 477.7 ns | 14.27 µs | **29.9x** | 2.94 µs | 193.59 µs | **66.0x** |
| 1,000,000 | 520.50 ms | 5.06 s | **9.72x** | 1.26 µs | 21.94 µs | **17.4x** | 670.7 ns | 14.12 µs | **21.1x** | 6.35 µs | 556.65 µs | **87.7x** |

### Detailed C++ GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | Batch (`closest_indices`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.254 ms | 265.8 ns | 299.2 ns | 265.5 ns | 1.52 µs | 3,761,720 qps | 3,766,546 qps | 659,510 qps |
| 10,000 | 3.71 ms | 360.4 ns | 397.7 ns | 349.5 ns | 1.91 µs | 2,774,434 qps | 2,861,173 qps | 523,048 qps |
| 100,000 | 42.75 ms | 526.2 ns | 569.6 ns | 477.7 ns | 2.94 µs | 1,900,378 qps | 2,093,368 qps | 340,676 qps |
| 1,000,000 | 520.50 ms | 1.26 µs | 736.5 ns | 670.7 ns | 6.35 µs | 793,713 qps | 1,490,924 qps | 157,545 qps |

### Detailed Pure Python GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | Batch (`closest_indices`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1.32 ms | 7.51 µs | 7.50 µs | 7.86 µs | 49.60 µs | 133,213 qps | 127,190 qps | 20,162 qps |
| 10,000 | 17.15 ms | 9.75 µs | 9.85 µs | 10.09 µs | 78.00 µs | 102,532 qps | 99,084 qps | 12,820 qps |
| 100,000 | 256.88 ms | 14.94 µs | 13.98 µs | 14.27 µs | 193.59 µs | 66,927 qps | 70,054 qps | 5,165 qps |
| 1,000,000 | 5.06 s | 21.94 µs | 14.34 µs | 14.12 µs | 556.65 µs | 45,570 qps | 70,815 qps | 1,796 qps |


## KDTree Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Batch | Python Batch | Batch Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.023 ms | 0.114 ms | **4.91x** | 214.7 ns | 4.02 µs | **18.7x** | 224.7 ns | 4.24 µs | **18.9x** | 825.9 ns | 20.11 µs | **24.3x** |
| 1,000 | 0.219 ms | 0.950 ms | **4.33x** | 315.5 ns | 5.34 µs | **16.9x** | 332.3 ns | 5.64 µs | **17.0x** | 1.03 µs | 17.51 µs | **16.9x** |
| 10,000 | 2.04 ms | 16.39 ms | **8.05x** | 352.7 ns | 7.07 µs | **20.1x** | 375.8 ns | 7.00 µs | **18.6x** | 1.19 µs | 20.63 µs | **17.3x** |
| 100,000 | 24.46 ms | 212.16 ms | **8.67x** | 456.5 ns | 9.69 µs | **21.2x** | 406.0 ns | 8.55 µs | **21.1x** | 1.86 µs | 25.87 µs | **13.9x** |
| 1,000,000 | 304.35 ms | 4.66 s | **15.33x** | 1.22 µs | 15.23 µs | **12.4x** | 660.2 ns | 9.57 µs | **14.5x** | 1.65 µs | 27.57 µs | **16.7x** |
### Detailed C++ KDTree Results

| Points ($N$) | Build Time | `closest_point` | Batch (`closest_points`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.023 ms | 214.7 ns | 224.7 ns | 825.9 ns | 4,657,562 qps | 4,449,590 qps | 1,210,736 qps |
| 1,000 | 0.219 ms | 315.5 ns | 332.3 ns | 1.03 µs | 3,169,527 qps | 3,009,761 qps | 966,318 qps |
| 10,000 | 2.04 ms | 352.7 ns | 375.8 ns | 1.19 µs | 2,835,148 qps | 2,660,754 qps | 840,749 qps |
| 100,000 | 24.46 ms | 456.5 ns | 406.0 ns | 1.86 µs | 2,190,345 qps | 2,463,096 qps | 538,246 qps |
| 1,000,000 | 304.35 ms | 1.22 µs | 660.2 ns | 1.65 µs | 817,006 qps | 1,514,795 qps | 605,347 qps |

### Detailed Pure Python KDTree Results

| Points ($N$) | Build Time | `closest_point` | Batch (`closest_points`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.114 ms | 4.02 µs | 4.24 µs | 20.11 µs | 248,516 qps | 235,841 qps | 49,728 qps |
| 1,000 | 0.950 ms | 5.34 µs | 5.64 µs | 17.51 µs | 187,312 qps | 177,354 qps | 57,115 qps |
| 10,000 | 16.39 ms | 7.07 µs | 7.00 µs | 20.63 µs | 141,382 qps | 142,859 qps | 48,468 qps |
| 100,000 | 212.16 ms | 9.69 µs | 8.55 µs | 25.87 µs | 103,235 qps | 116,895 qps | 38,649 qps |
| 1,000,000 | 4.66 s | 15.23 µs | 9.57 µs | 27.57 µs | 65,666 qps | 104,506 qps | 36,274 qps |


## GeoHilbert Benchmarks (Latitude/Longitude)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.441 ms | 18.74 ms | **42.46x** | 434.0 ns | 22.98 µs | **53.0x** | 0.023 ms | 0.007 ms | **0.3x** |
| 10,000 | 4.50 ms | 189.78 ms | **42.17x** | 445.4 ns | 23.02 µs | **51.7x** | 0.181 ms | 0.026 ms | **0.1x** |
| 100,000 | 46.60 ms | 1.87 s | **40.22x** | 464.8 ns | 23.03 µs | **49.5x** | 2.08 ms | 0.631 ms | **0.3x** |
| 1,000,000 | 564.82 ms | 19.29 s | **34.15x** | 570.0 ns | 23.70 µs | **41.6x** | 19.92 ms | 14.28 ms | **0.7x** |

### Detailed C++ GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.441 ms | 434.0 ns | 397.9 ns | 387.4 ns | 0.023 ms | 2,304,042 qps | 2,581,531 qps |
| 10,000 | 4.50 ms | 445.4 ns | 415.5 ns | 390.4 ns | 0.181 ms | 2,245,064 qps | 2,561,206 qps |
| 100,000 | 46.60 ms | 464.8 ns | 455.5 ns | 445.3 ns | 2.08 ms | 2,151,259 qps | 2,245,893 qps |
| 1,000,000 | 564.82 ms | 570.0 ns | 650.4 ns | 592.3 ns | 19.92 ms | 1,754,278 qps | 1,688,390 qps |

### Detailed Pure Python GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 18.74 ms | 22.98 µs | 22.98 µs | 23.15 µs | 0.007 ms | 43,511 qps | 43,196 qps |
| 10,000 | 189.78 ms | 23.02 µs | 23.10 µs | 23.12 µs | 0.026 ms | 43,448 qps | 43,260 qps |
| 100,000 | 1.87 s | 23.03 µs | 23.86 µs | 23.07 µs | 0.631 ms | 43,419 qps | 43,345 qps |
| 1,000,000 | 19.29 s | 23.70 µs | 26.34 µs | 23.60 µs | 14.28 ms | 42,200 qps | 42,368 qps |


## Hilbert Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.399 ms | 11.52 ms | **28.86x** | 409.4 ns | 14.69 µs | **35.9x** | 0.022 ms | 0.007 ms | **0.3x** |
| 10,000 | 3.92 ms | 114.60 ms | **29.22x** | 421.6 ns | 14.44 µs | **34.3x** | 0.181 ms | 0.027 ms | **0.1x** |
| 100,000 | 42.71 ms | 1.15 s | **26.87x** | 451.2 ns | 14.75 µs | **32.7x** | 2.07 ms | 0.591 ms | **0.3x** |
| 1,000,000 | 520.58 ms | 11.87 s | **22.80x** | 617.7 ns | 14.95 µs | **24.2x** | 31.28 ms | 15.12 ms | **0.5x** |

### Detailed C++ Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.399 ms | 409.4 ns | 347.6 ns | 379.3 ns | 0.022 ms | 2,442,496 qps | 2,636,228 qps |
| 10,000 | 3.92 ms | 421.6 ns | 366.1 ns | 397.2 ns | 0.181 ms | 2,371,949 qps | 2,517,713 qps |
| 100,000 | 42.71 ms | 451.2 ns | 390.9 ns | 404.8 ns | 2.07 ms | 2,216,366 qps | 2,470,227 qps |
| 1,000,000 | 520.58 ms | 617.7 ns | 585.9 ns | 471.7 ns | 31.28 ms | 1,618,843 qps | 2,119,789 qps |

### Detailed Pure Python Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 11.52 ms | 14.69 µs | 14.62 µs | 14.88 µs | 0.007 ms | 68,081 qps | 67,222 qps |
| 10,000 | 114.60 ms | 14.44 µs | 14.56 µs | 14.80 µs | 0.027 ms | 69,244 qps | 67,565 qps |
| 100,000 | 1.15 s | 14.75 µs | 15.24 µs | 14.96 µs | 0.591 ms | 67,814 qps | 66,836 qps |
| 1,000,000 | 11.87 s | 14.95 µs | 17.64 µs | 15.70 µs | 15.12 ms | 66,905 qps | 63,692 qps |


## Methodology

1. **Data**: Coordinates randomly and uniformly distributed over valid ranges ($[-90, 90]$ latitude, $[-180, 180]$ longitude for GeoKDTree and GeoHilbert; $[0, 1000] \times [0, 1000]$ for 2D KDTree and Hilbert).
2. **Timing**: Measured with `time.perf_counter()` over thousands of repeated lookups to compute stable averages.
3. **Reproducibility**: Run `uv run python utils/benchmark.py` to regenerate these benchmarks on your hardware.
