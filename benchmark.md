# GeoKDTree Performance Benchmarks

Automated performance benchmarks for `geokdtree` comparing C++ and Pure Python implementations across various dataset scales.

## Environment

| Attribute | Value |
|---|---|
| **Date** | 2026-11-20 20:55:58 UTC |
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
| 1,000 | 0.218 ms | 1.33 ms | **6.11x** | 279.8 ns | 7.58 µs | **27.1x** | 271.1 ns | 7.92 µs | **29.2x** | 1.53 µs | 50.43 µs | **33.0x** |
| 10,000 | 3.42 ms | 17.29 ms | **5.05x** | 374.4 ns | 9.92 µs | **26.5x** | 345.3 ns | 10.12 µs | **29.3x** | 1.91 µs | 79.40 µs | **41.5x** |
| 100,000 | 40.04 ms | 278.19 ms | **6.95x** | 574.5 ns | 16.91 µs | **29.4x** | 456.0 ns | 15.45 µs | **33.9x** | 3.01 µs | 211.97 µs | **70.5x** |
| 1,000,000 | 475.60 ms | 5.18 s | **10.90x** | 1.37 µs | 21.78 µs | **15.9x** | 662.7 ns | 14.31 µs | **21.6x** | 6.44 µs | 558.73 µs | **86.7x** |

### Detailed C++ GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | Batch (`closest_indices`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.218 ms | 279.8 ns | 290.2 ns | 271.1 ns | 1.53 µs | 3,573,358 qps | 3,688,322 qps | 654,679 qps |
| 10,000 | 3.42 ms | 374.4 ns | 394.4 ns | 345.3 ns | 1.91 µs | 2,670,821 qps | 2,896,274 qps | 522,410 qps |
| 100,000 | 40.04 ms | 574.5 ns | 580.9 ns | 456.0 ns | 3.01 µs | 1,740,725 qps | 2,193,040 qps | 332,767 qps |
| 1,000,000 | 475.60 ms | 1.37 µs | 761.3 ns | 662.7 ns | 6.44 µs | 728,324 qps | 1,508,955 qps | 155,247 qps |

### Detailed Pure Python GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | Batch (`closest_indices`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1.33 ms | 7.58 µs | 7.59 µs | 7.92 µs | 50.43 µs | 131,958 qps | 126,233 qps | 19,830 qps |
| 10,000 | 17.29 ms | 9.92 µs | 10.11 µs | 10.12 µs | 79.40 µs | 100,774 qps | 98,790 qps | 12,594 qps |
| 100,000 | 278.19 ms | 16.91 µs | 15.60 µs | 15.45 µs | 211.97 µs | 59,130 qps | 64,710 qps | 4,717 qps |
| 1,000,000 | 5.18 s | 21.78 µs | 14.36 µs | 14.31 µs | 558.73 µs | 45,910 qps | 69,864 qps | 1,789 qps |


## KDTree Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Batch | Python Batch | Batch Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.021 ms | 0.102 ms | **4.87x** | 231.4 ns | 4.04 µs | **17.4x** | 241.6 ns | 4.35 µs | **18.0x** | 872.2 ns | 21.35 µs | **24.5x** |
| 1,000 | 0.160 ms | 0.987 ms | **6.19x** | 311.8 ns | 5.50 µs | **17.6x** | 393.7 ns | 5.63 µs | **14.3x** | 1.13 µs | 17.74 µs | **15.7x** |
| 10,000 | 1.81 ms | 15.65 ms | **8.63x** | 360.0 ns | 6.81 µs | **18.9x** | 369.1 ns | 7.08 µs | **19.2x** | 1.23 µs | 20.86 µs | **17.0x** |
| 100,000 | 21.41 ms | 220.19 ms | **10.29x** | 510.4 ns | 10.07 µs | **19.7x** | 428.1 ns | 8.95 µs | **20.9x** | 1.43 µs | 27.19 µs | **19.0x** |
| 1,000,000 | 270.02 ms | 4.96 s | **18.37x** | 1.24 µs | 14.97 µs | **12.1x** | 669.6 ns | 9.68 µs | **14.5x** | 1.76 µs | 27.82 µs | **15.8x** |
### Detailed C++ KDTree Results

| Points ($N$) | Build Time | `closest_point` | Batch (`closest_points`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.021 ms | 231.4 ns | 241.6 ns | 872.2 ns | 4,322,223 qps | 4,138,493 qps | 1,146,509 qps |
| 1,000 | 0.160 ms | 311.8 ns | 393.7 ns | 1.13 µs | 3,207,272 qps | 2,539,904 qps | 885,094 qps |
| 10,000 | 1.81 ms | 360.0 ns | 369.1 ns | 1.23 µs | 2,777,598 qps | 2,709,097 qps | 812,780 qps |
| 100,000 | 21.41 ms | 510.4 ns | 428.1 ns | 1.43 µs | 1,959,278 qps | 2,336,099 qps | 698,018 qps |
| 1,000,000 | 270.02 ms | 1.24 µs | 669.6 ns | 1.76 µs | 806,705 qps | 1,493,373 qps | 568,294 qps |

### Detailed Pure Python KDTree Results

| Points ($N$) | Build Time | `closest_point` | Batch (`closest_points`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.102 ms | 4.04 µs | 4.35 µs | 21.35 µs | 247,785 qps | 229,735 qps | 46,842 qps |
| 1,000 | 0.987 ms | 5.50 µs | 5.63 µs | 17.74 µs | 181,769 qps | 177,543 qps | 56,355 qps |
| 10,000 | 15.65 ms | 6.81 µs | 7.08 µs | 20.86 µs | 146,905 qps | 141,308 qps | 47,940 qps |
| 100,000 | 220.19 ms | 10.07 µs | 8.95 µs | 27.19 µs | 99,288 qps | 111,770 qps | 36,784 qps |
| 1,000,000 | 4.96 s | 14.97 µs | 9.68 µs | 27.82 µs | 66,804 qps | 103,287 qps | 35,945 qps |


## GeoHilbert Benchmarks (Latitude/Longitude)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.438 ms | 18.78 ms | **42.88x** | 432.4 ns | 22.90 µs | **53.0x** | 0.026 ms | 0.008 ms | **0.3x** |
| 10,000 | 4.35 ms | 191.13 ms | **43.97x** | 451.6 ns | 23.37 µs | **51.8x** | 0.213 ms | 0.079 ms | **0.4x** |
| 100,000 | 43.40 ms | 1.92 s | **44.21x** | 504.7 ns | 23.34 µs | **46.2x** | 2.12 ms | 0.628 ms | **0.3x** |
| 1,000,000 | 465.91 ms | 19.42 s | **41.69x** | 662.0 ns | 24.20 µs | **36.6x** | 21.09 ms | 15.93 ms | **0.8x** |

### Detailed C++ GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.438 ms | 432.4 ns | 402.7 ns | 387.3 ns | 0.026 ms | 2,312,410 qps | 2,582,251 qps |
| 10,000 | 4.35 ms | 451.6 ns | 430.8 ns | 393.4 ns | 0.213 ms | 2,214,488 qps | 2,541,962 qps |
| 100,000 | 43.40 ms | 504.7 ns | 435.1 ns | 428.1 ns | 2.12 ms | 1,981,410 qps | 2,335,706 qps |
| 1,000,000 | 465.91 ms | 662.0 ns | 686.1 ns | 1.15 µs | 21.09 ms | 1,510,665 qps | 873,148 qps |

### Detailed Pure Python GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 18.78 ms | 22.90 µs | 22.82 µs | 23.14 µs | 0.008 ms | 43,670 qps | 43,222 qps |
| 10,000 | 191.13 ms | 23.37 µs | 23.72 µs | 23.84 µs | 0.079 ms | 42,785 qps | 41,944 qps |
| 100,000 | 1.92 s | 23.34 µs | 24.08 µs | 23.40 µs | 0.628 ms | 42,842 qps | 42,741 qps |
| 1,000,000 | 19.42 s | 24.20 µs | 26.51 µs | 23.97 µs | 15.93 ms | 41,320 qps | 41,721 qps |


## Hilbert Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.384 ms | 11.52 ms | **30.03x** | 417.3 ns | 14.69 µs | **35.2x** | 0.022 ms | 0.008 ms | **0.4x** |
| 10,000 | 3.87 ms | 116.29 ms | **30.08x** | 439.2 ns | 15.02 µs | **34.2x** | 0.181 ms | 0.069 ms | **0.4x** |
| 100,000 | 40.75 ms | 1.17 s | **28.60x** | 470.9 ns | 14.77 µs | **31.4x** | 2.16 ms | 0.844 ms | **0.4x** |
| 1,000,000 | 474.50 ms | 11.82 s | **24.90x** | 688.0 ns | 14.96 µs | **21.7x** | 28.55 ms | 15.31 ms | **0.5x** |

### Detailed C++ Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.384 ms | 417.3 ns | 373.7 ns | 378.1 ns | 0.022 ms | 2,396,471 qps | 2,644,790 qps |
| 10,000 | 3.87 ms | 439.2 ns | 376.5 ns | 406.5 ns | 0.181 ms | 2,277,032 qps | 2,459,928 qps |
| 100,000 | 40.75 ms | 470.9 ns | 415.7 ns | 428.7 ns | 2.16 ms | 2,123,746 qps | 2,332,600 qps |
| 1,000,000 | 474.50 ms | 688.0 ns | 622.9 ns | 506.9 ns | 28.55 ms | 1,453,467 qps | 1,972,717 qps |

### Detailed Pure Python Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 11.52 ms | 14.69 µs | 14.88 µs | 14.83 µs | 0.008 ms | 68,057 qps | 67,412 qps |
| 10,000 | 116.29 ms | 15.02 µs | 15.28 µs | 15.34 µs | 0.069 ms | 66,559 qps | 65,189 qps |
| 100,000 | 1.17 s | 14.77 µs | 16.05 µs | 14.99 µs | 0.844 ms | 67,715 qps | 66,723 qps |
| 1,000,000 | 11.82 s | 14.96 µs | 18.53 µs | 15.11 µs | 15.31 ms | 66,848 qps | 66,195 qps |


## Methodology

1. **Data**: Coordinates randomly and uniformly distributed over valid ranges ($[-90, 90]$ latitude, $[-180, 180]$ longitude for GeoKDTree and GeoHilbert; $[0, 1000] \times [0, 1000]$ for 2D KDTree and Hilbert).
2. **Timing**: Measured with `time.perf_counter()` over thousands of repeated lookups to compute stable averages.
3. **Reproducibility**: Run `uv run python utils/benchmark.py` to regenerate these benchmarks on your hardware.
