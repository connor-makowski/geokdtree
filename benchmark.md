# GeoKDTree Performance Benchmarks

Automated performance benchmarks for `geokdtree` comparing C++ and Pure Python implementations across various dataset scales.

## Environment

| Attribute | Value |
|---|---|
| **Date** | 2026-11-20 21:04:19 UTC |
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
| 1,000 | 0.210 ms | 1.33 ms | **6.35x** | 275.6 ns | 7.63 µs | **27.7x** | 262.5 ns | 7.88 µs | **30.0x** | 1.57 µs | 50.46 µs | **32.2x** |
| 10,000 | 3.44 ms | 17.26 ms | **5.02x** | 370.2 ns | 10.05 µs | **27.1x** | 343.7 ns | 10.21 µs | **29.7x** | 1.95 µs | 82.63 µs | **42.3x** |
| 100,000 | 40.06 ms | 271.08 ms | **6.77x** | 551.3 ns | 15.44 µs | **28.0x** | 460.0 ns | 16.23 µs | **35.3x** | 2.94 µs | 202.26 µs | **68.9x** |
| 1,000,000 | 473.85 ms | 5.36 s | **11.32x** | 1.43 µs | 22.21 µs | **15.5x** | 650.6 ns | 15.96 µs | **24.5x** | 6.27 µs | 568.34 µs | **90.6x** |

### Detailed C++ GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | Batch (`closest_indices`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.210 ms | 275.6 ns | 308.5 ns | 262.5 ns | 1.57 µs | 3,628,175 qps | 3,809,120 qps | 638,974 qps |
| 10,000 | 3.44 ms | 370.2 ns | 400.2 ns | 343.7 ns | 1.95 µs | 2,700,930 qps | 2,909,461 qps | 511,545 qps |
| 100,000 | 40.06 ms | 551.3 ns | 572.1 ns | 460.0 ns | 2.94 µs | 1,813,963 qps | 2,174,078 qps | 340,679 qps |
| 1,000,000 | 473.85 ms | 1.43 µs | 719.9 ns | 650.6 ns | 6.27 µs | 699,633 qps | 1,537,066 qps | 159,469 qps |

### Detailed Pure Python GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | Batch (`closest_indices`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1.33 ms | 7.63 µs | 7.87 µs | 7.88 µs | 50.46 µs | 131,123 qps | 126,954 qps | 19,817 qps |
| 10,000 | 17.26 ms | 10.05 µs | 9.96 µs | 10.21 µs | 82.63 µs | 99,490 qps | 97,956 qps | 12,102 qps |
| 100,000 | 271.08 ms | 15.44 µs | 15.20 µs | 16.23 µs | 202.26 µs | 64,770 qps | 61,619 qps | 4,944 qps |
| 1,000,000 | 5.36 s | 22.21 µs | 14.48 µs | 15.96 µs | 568.34 µs | 45,028 qps | 62,661 qps | 1,759 qps |


## KDTree Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Batch | Python Batch | Batch Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.022 ms | 0.093 ms | **4.29x** | 211.0 ns | 4.11 µs | **19.5x** | 260.2 ns | 4.33 µs | **16.6x** | 847.4 ns | 20.39 µs | **24.1x** |
| 1,000 | 0.154 ms | 0.970 ms | **6.28x** | 295.7 ns | 5.43 µs | **18.4x** | 323.2 ns | 5.61 µs | **17.4x** | 1.07 µs | 17.94 µs | **16.8x** |
| 10,000 | 1.79 ms | 15.99 ms | **8.93x** | 359.4 ns | 6.79 µs | **18.9x** | 386.9 ns | 7.13 µs | **18.4x** | 1.21 µs | 21.96 µs | **18.1x** |
| 100,000 | 21.38 ms | 222.61 ms | **10.41x** | 542.9 ns | 9.82 µs | **18.1x** | 455.8 ns | 9.08 µs | **19.9x** | 1.46 µs | 27.29 µs | **18.7x** |
| 1,000,000 | 267.23 ms | 4.76 s | **17.83x** | 1.16 µs | 14.84 µs | **12.8x** | 633.1 ns | 10.06 µs | **15.9x** | 1.68 µs | 27.82 µs | **16.5x** |
### Detailed C++ KDTree Results

| Points ($N$) | Build Time | `closest_point` | Batch (`closest_points`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.022 ms | 211.0 ns | 260.2 ns | 847.4 ns | 4,738,986 qps | 3,842,763 qps | 1,180,070 qps |
| 1,000 | 0.154 ms | 295.7 ns | 323.2 ns | 1.07 µs | 3,382,048 qps | 3,093,933 qps | 935,481 qps |
| 10,000 | 1.79 ms | 359.4 ns | 386.9 ns | 1.21 µs | 2,782,057 qps | 2,584,683 qps | 825,427 qps |
| 100,000 | 21.38 ms | 542.9 ns | 455.8 ns | 1.46 µs | 1,841,912 qps | 2,193,761 qps | 686,009 qps |
| 1,000,000 | 267.23 ms | 1.16 µs | 633.1 ns | 1.68 µs | 862,697 qps | 1,579,516 qps | 594,546 qps |

### Detailed Pure Python KDTree Results

| Points ($N$) | Build Time | `closest_point` | Batch (`closest_points`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.093 ms | 4.11 µs | 4.33 µs | 20.39 µs | 243,541 qps | 231,177 qps | 49,033 qps |
| 1,000 | 0.970 ms | 5.43 µs | 5.61 µs | 17.94 µs | 184,189 qps | 178,108 qps | 55,730 qps |
| 10,000 | 15.99 ms | 6.79 µs | 7.13 µs | 21.96 µs | 147,193 qps | 140,259 qps | 45,532 qps |
| 100,000 | 222.61 ms | 9.82 µs | 9.08 µs | 27.29 µs | 101,819 qps | 110,134 qps | 36,647 qps |
| 1,000,000 | 4.76 s | 14.84 µs | 10.06 µs | 27.82 µs | 67,388 qps | 99,397 qps | 35,943 qps |


## GeoHilbert Benchmarks (Latitude/Longitude)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.444 ms | 20.22 ms | **45.59x** | 444.8 ns | 23.12 µs | **52.0x** | 0.024 ms | 0.008 ms | **0.4x** |
| 10,000 | 4.28 ms | 201.77 ms | **47.19x** | 486.6 ns | 23.44 µs | **48.2x** | 0.218 ms | 0.076 ms | **0.3x** |
| 100,000 | 43.43 ms | 2.02 s | **46.55x** | 557.7 ns | 24.21 µs | **43.4x** | 2.30 ms | 0.617 ms | **0.3x** |
| 1,000,000 | 471.41 ms | 20.62 s | **43.75x** | 686.4 ns | 23.60 µs | **34.4x** | 22.17 ms | 14.79 ms | **0.7x** |

### Detailed C++ GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.444 ms | 444.8 ns | 405.2 ns | 385.1 ns | 0.024 ms | 2,248,117 qps | 2,597,005 qps |
| 10,000 | 4.28 ms | 486.6 ns | 475.9 ns | 404.1 ns | 0.218 ms | 2,054,931 qps | 2,474,774 qps |
| 100,000 | 43.43 ms | 557.7 ns | 443.0 ns | 440.0 ns | 2.30 ms | 1,793,104 qps | 2,272,685 qps |
| 1,000,000 | 471.41 ms | 686.4 ns | 937.6 ns | 592.6 ns | 22.17 ms | 1,456,961 qps | 1,687,550 qps |

### Detailed Pure Python GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 20.22 ms | 23.12 µs | 23.04 µs | 23.38 µs | 0.008 ms | 43,257 qps | 42,765 qps |
| 10,000 | 201.77 ms | 23.44 µs | 23.18 µs | 23.64 µs | 0.076 ms | 42,660 qps | 42,309 qps |
| 100,000 | 2.02 s | 24.21 µs | 24.23 µs | 23.35 µs | 0.617 ms | 41,307 qps | 42,832 qps |
| 1,000,000 | 20.62 s | 23.60 µs | 26.40 µs | 23.47 µs | 14.79 ms | 42,368 qps | 42,604 qps |


## Hilbert Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.398 ms | 11.90 ms | **29.91x** | 432.3 ns | 15.21 µs | **35.2x** | 0.024 ms | 0.009 ms | **0.4x** |
| 10,000 | 3.96 ms | 120.35 ms | **30.35x** | 458.1 ns | 15.80 µs | **34.5x** | 0.219 ms | 0.050 ms | **0.2x** |
| 100,000 | 41.55 ms | 1.19 s | **28.67x** | 471.0 ns | 15.56 µs | **33.0x** | 2.59 ms | 0.684 ms | **0.3x** |
| 1,000,000 | 478.98 ms | 11.90 s | **24.85x** | 649.7 ns | 14.72 µs | **22.7x** | 27.93 ms | 14.80 ms | **0.5x** |

### Detailed C++ Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.398 ms | 432.3 ns | 391.8 ns | 388.7 ns | 0.024 ms | 2,312,946 qps | 2,572,851 qps |
| 10,000 | 3.96 ms | 458.1 ns | 391.3 ns | 415.7 ns | 0.219 ms | 2,182,987 qps | 2,405,330 qps |
| 100,000 | 41.55 ms | 471.0 ns | 440.1 ns | 422.4 ns | 2.59 ms | 2,123,065 qps | 2,367,289 qps |
| 1,000,000 | 478.98 ms | 649.7 ns | 577.9 ns | 490.1 ns | 27.93 ms | 1,539,207 qps | 2,040,254 qps |

### Detailed Pure Python Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 11.90 ms | 15.21 µs | 15.19 µs | 15.51 µs | 0.009 ms | 65,756 qps | 64,494 qps |
| 10,000 | 120.35 ms | 15.80 µs | 15.82 µs | 15.93 µs | 0.050 ms | 63,303 qps | 62,760 qps |
| 100,000 | 1.19 s | 15.56 µs | 15.89 µs | 16.02 µs | 0.684 ms | 64,273 qps | 62,412 qps |
| 1,000,000 | 11.90 s | 14.72 µs | 17.64 µs | 14.94 µs | 14.80 ms | 67,928 qps | 66,922 qps |


## Methodology

1. **Data**: Coordinates randomly and uniformly distributed over valid ranges ($[-90, 90]$ latitude, $[-180, 180]$ longitude for GeoKDTree and GeoHilbert; $[0, 1000] \times [0, 1000]$ for 2D KDTree and Hilbert).
2. **Timing**: Measured with `time.perf_counter()` over thousands of repeated lookups to compute stable averages.
3. **Reproducibility**: Run `uv run python utils/benchmark.py` to regenerate these benchmarks on your hardware.
