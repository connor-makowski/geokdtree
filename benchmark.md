# GeoKDTree Performance Benchmarks

Automated performance benchmarks for `geokdtree` comparing C++ and Pure Python implementations across various dataset scales.

## Environment

| Attribute | Value |
|---|---|
| **Date** | 2026-11-20 18:22:02 UTC |
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
| 1,000 | 0.228 ms | 1.33 ms | **5.81x** | 279.5 ns | 7.60 µs | **27.2x** | 262.3 ns | 7.82 µs | **29.8x** | 1.51 µs | 50.29 µs | **33.2x** |
| 10,000 | 3.65 ms | 17.39 ms | **4.77x** | 373.0 ns | 10.08 µs | **27.0x** | 342.6 ns | 10.37 µs | **30.3x** | 1.91 µs | 82.56 µs | **43.3x** |
| 100,000 | 43.51 ms | 270.05 ms | **6.21x** | 627.7 ns | 15.35 µs | **24.5x** | 561.5 ns | 15.24 µs | **27.1x** | 3.37 µs | 216.09 µs | **64.1x** |
| 1,000,000 | 516.64 ms | 5.16 s | **9.98x** | 1.31 µs | 21.80 µs | **16.6x** | 660.2 ns | 13.89 µs | **21.0x** | 6.30 µs | 556.83 µs | **88.4x** |

### Detailed C++ GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | Batch (`closest_indices`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.228 ms | 279.5 ns | 306.6 ns | 262.3 ns | 1.51 µs | 3,577,725 qps | 3,812,914 qps | 660,174 qps |
| 10,000 | 3.65 ms | 373.0 ns | 400.2 ns | 342.6 ns | 1.91 µs | 2,680,871 qps | 2,919,220 qps | 524,581 qps |
| 100,000 | 43.51 ms | 627.7 ns | 595.1 ns | 561.5 ns | 3.37 µs | 1,593,237 qps | 1,780,794 qps | 296,671 qps |
| 1,000,000 | 516.64 ms | 1.31 µs | 731.7 ns | 660.2 ns | 6.30 µs | 762,227 qps | 1,514,681 qps | 158,844 qps |

### Detailed Pure Python GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | Batch (`closest_indices`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1.33 ms | 7.60 µs | 7.70 µs | 7.82 µs | 50.29 µs | 131,506 qps | 127,816 qps | 19,884 qps |
| 10,000 | 17.39 ms | 10.08 µs | 10.16 µs | 10.37 µs | 82.56 µs | 99,215 qps | 96,450 qps | 12,112 qps |
| 100,000 | 270.05 ms | 15.35 µs | 15.12 µs | 15.24 µs | 216.09 µs | 65,139 qps | 65,613 qps | 4,627 qps |
| 1,000,000 | 5.16 s | 21.80 µs | 15.13 µs | 13.89 µs | 556.83 µs | 45,877 qps | 71,979 qps | 1,795 qps |


## KDTree Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Batch | Python Batch | Batch Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.023 ms | 0.104 ms | **4.46x** | 209.8 ns | 3.96 µs | **18.9x** | 229.6 ns | 4.24 µs | **18.5x** | 829.7 ns | 20.42 µs | **24.6x** |
| 1,000 | 0.172 ms | 0.974 ms | **5.67x** | 278.4 ns | 5.32 µs | **19.1x** | 302.2 ns | 5.59 µs | **18.5x** | 1.04 µs | 17.49 µs | **16.8x** |
| 10,000 | 2.04 ms | 15.56 ms | **7.64x** | 344.1 ns | 6.74 µs | **19.6x** | 353.3 ns | 6.99 µs | **19.8x** | 1.18 µs | 20.78 µs | **17.6x** |
| 100,000 | 24.78 ms | 222.50 ms | **8.98x** | 548.9 ns | 9.67 µs | **17.6x** | 434.4 ns | 9.84 µs | **22.6x** | 1.44 µs | 27.30 µs | **19.0x** |
| 1,000,000 | 309.26 ms | 5.02 s | **16.23x** | 1.19 µs | 16.00 µs | **13.4x** | 666.0 ns | 9.46 µs | **14.2x** | 1.73 µs | 29.41 µs | **17.0x** |
### Detailed C++ KDTree Results

| Points ($N$) | Build Time | `closest_point` | Batch (`closest_points`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.023 ms | 209.8 ns | 229.6 ns | 829.7 ns | 4,767,425 qps | 4,355,127 qps | 1,205,232 qps |
| 1,000 | 0.172 ms | 278.4 ns | 302.2 ns | 1.04 µs | 3,591,448 qps | 3,308,666 qps | 962,632 qps |
| 10,000 | 2.04 ms | 344.1 ns | 353.3 ns | 1.18 µs | 2,906,537 qps | 2,830,523 qps | 848,067 qps |
| 100,000 | 24.78 ms | 548.9 ns | 434.4 ns | 1.44 µs | 1,821,881 qps | 2,301,888 qps | 696,441 qps |
| 1,000,000 | 309.26 ms | 1.19 µs | 666.0 ns | 1.73 µs | 837,822 qps | 1,501,580 qps | 576,686 qps |

### Detailed Pure Python KDTree Results

| Points ($N$) | Build Time | `closest_point` | Batch (`closest_points`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.104 ms | 3.96 µs | 4.24 µs | 20.42 µs | 252,407 qps | 235,611 qps | 48,970 qps |
| 1,000 | 0.974 ms | 5.32 µs | 5.59 µs | 17.49 µs | 187,961 qps | 178,911 qps | 57,187 qps |
| 10,000 | 15.56 ms | 6.74 µs | 6.99 µs | 20.78 µs | 148,264 qps | 143,110 qps | 48,113 qps |
| 100,000 | 222.50 ms | 9.67 µs | 9.84 µs | 27.30 µs | 103,403 qps | 101,634 qps | 36,633 qps |
| 1,000,000 | 5.02 s | 16.00 µs | 9.46 µs | 29.41 µs | 62,506 qps | 105,721 qps | 33,996 qps |


## GeoHilbert Benchmarks (Latitude/Longitude)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.467 ms | 18.91 ms | **40.51x** | 429.6 ns | 22.91 µs | **53.3x** | 0.022 ms | 0.008 ms | **0.4x** |
| 10,000 | 4.56 ms | 189.02 ms | **41.46x** | 440.3 ns | 23.15 µs | **52.6x** | 0.223 ms | 0.038 ms | **0.2x** |
| 100,000 | 48.54 ms | 1.89 s | **39.00x** | 482.0 ns | 24.35 µs | **50.5x** | 2.09 ms | 0.677 ms | **0.3x** |
| 1,000,000 | 579.26 ms | 19.42 s | **33.53x** | 588.3 ns | 24.48 µs | **41.6x** | 23.58 ms | 14.94 ms | **0.6x** |

### Detailed C++ GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.467 ms | 429.6 ns | 414.2 ns | 397.9 ns | 0.022 ms | 2,328,015 qps | 2,513,104 qps |
| 10,000 | 4.56 ms | 440.3 ns | 417.1 ns | 418.4 ns | 0.223 ms | 2,271,101 qps | 2,390,279 qps |
| 100,000 | 48.54 ms | 482.0 ns | 457.6 ns | 460.4 ns | 2.09 ms | 2,074,835 qps | 2,171,807 qps |
| 1,000,000 | 579.26 ms | 588.3 ns | 646.0 ns | 621.7 ns | 23.58 ms | 1,699,899 qps | 1,608,531 qps |

### Detailed Pure Python GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 18.91 ms | 22.91 µs | 22.90 µs | 23.28 µs | 0.008 ms | 43,641 qps | 42,957 qps |
| 10,000 | 189.02 ms | 23.15 µs | 23.12 µs | 23.26 µs | 0.038 ms | 43,201 qps | 42,992 qps |
| 100,000 | 1.89 s | 24.35 µs | 24.51 µs | 24.27 µs | 0.677 ms | 41,073 qps | 41,196 qps |
| 1,000,000 | 19.42 s | 24.48 µs | 27.95 µs | 23.11 µs | 14.94 ms | 40,843 qps | 43,273 qps |


## Hilbert Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.405 ms | 12.30 ms | **30.38x** | 410.9 ns | 14.57 µs | **35.5x** | 0.021 ms | 0.008 ms | **0.4x** |
| 10,000 | 4.03 ms | 123.06 ms | **30.57x** | 422.1 ns | 14.68 µs | **34.8x** | 0.182 ms | 0.028 ms | **0.2x** |
| 100,000 | 44.78 ms | 1.23 s | **27.53x** | 506.4 ns | 15.14 µs | **29.9x** | 2.40 ms | 0.614 ms | **0.3x** |
| 1,000,000 | 530.69 ms | 12.55 s | **23.65x** | 638.8 ns | 14.57 µs | **22.8x** | 30.76 ms | 14.77 ms | **0.5x** |

### Detailed C++ Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.405 ms | 410.9 ns | 371.4 ns | 378.0 ns | 0.021 ms | 2,433,852 qps | 2,645,666 qps |
| 10,000 | 4.03 ms | 422.1 ns | 378.0 ns | 401.9 ns | 0.182 ms | 2,368,902 qps | 2,488,342 qps |
| 100,000 | 44.78 ms | 506.4 ns | 559.7 ns | 432.7 ns | 2.40 ms | 1,974,559 qps | 2,311,005 qps |
| 1,000,000 | 530.69 ms | 638.8 ns | 671.0 ns | 482.4 ns | 30.76 ms | 1,565,398 qps | 2,072,904 qps |

### Detailed Pure Python Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 12.30 ms | 14.57 µs | 14.50 µs | 14.71 µs | 0.008 ms | 68,633 qps | 67,966 qps |
| 10,000 | 123.06 ms | 14.68 µs | 14.73 µs | 14.91 µs | 0.028 ms | 68,137 qps | 67,052 qps |
| 100,000 | 1.23 s | 15.14 µs | 15.46 µs | 15.35 µs | 0.614 ms | 66,057 qps | 65,146 qps |
| 1,000,000 | 12.55 s | 14.57 µs | 17.39 µs | 14.94 µs | 14.77 ms | 68,642 qps | 66,945 qps |


## Methodology

1. **Data**: Coordinates randomly and uniformly distributed over valid ranges ($[-90, 90]$ latitude, $[-180, 180]$ longitude for GeoKDTree and GeoHilbert; $[0, 1000] \times [0, 1000]$ for 2D KDTree and Hilbert).
2. **Timing**: Measured with `time.perf_counter()` over thousands of repeated lookups to compute stable averages.
3. **Reproducibility**: Run `uv run python utils/benchmark.py` to regenerate these benchmarks on your hardware.
