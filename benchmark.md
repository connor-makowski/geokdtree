# GeoKDTree Performance Benchmarks

Automated performance benchmarks for `geokdtree` comparing C++ and Pure Python implementations across various dataset scales.

## Environment

| Attribute | Value |
|---|---|
| **Date** | 2026-11-20 16:49:20 UTC |
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
| 1,000 | 0.251 ms | 1.32 ms | **5.25x** | 276.4 ns | 7.36 µs | **26.6x** | 1.48 µs | 48.49 µs | **32.7x** |
| 10,000 | 3.58 ms | 16.67 ms | **4.66x** | 359.9 ns | 9.48 µs | **26.3x** | 1.83 µs | 76.41 µs | **41.8x** |
| 100,000 | 41.70 ms | 258.04 ms | **6.19x** | 571.5 ns | 15.09 µs | **26.4x** | 3.10 µs | 197.87 µs | **63.7x** |
| 1,000,000 | 499.47 ms | 5.02 s | **10.05x** | 1.27 µs | 22.21 µs | **17.4x** | 6.30 µs | 576.71 µs | **91.6x** |

### Detailed C++ GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.251 ms | 276.4 ns | 304.7 ns | 1.48 µs | 3,618,180 qps | 673,763 qps |
| 10,000 | 3.58 ms | 359.9 ns | 387.7 ns | 1.83 µs | 2,778,356 qps | 547,224 qps |
| 100,000 | 41.70 ms | 571.5 ns | 572.0 ns | 3.10 µs | 1,749,664 qps | 322,086 qps |
| 1,000,000 | 499.47 ms | 1.27 µs | 755.1 ns | 6.30 µs | 785,437 qps | 158,809 qps |

### Detailed Pure Python GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1.32 ms | 7.36 µs | 7.42 µs | 48.49 µs | 135,781 qps | 20,623 qps |
| 10,000 | 16.67 ms | 9.48 µs | 9.58 µs | 76.41 µs | 105,445 qps | 13,086 qps |
| 100,000 | 258.04 ms | 15.09 µs | 14.48 µs | 197.87 µs | 66,289 qps | 5,053 qps |
| 1,000,000 | 5.02 s | 22.21 µs | 13.87 µs | 576.71 µs | 45,025 qps | 1,733 qps |


## KDTree Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.021 ms | 0.095 ms | **4.59x** | 212.0 ns | 3.92 µs | **18.5x** | 820.6 ns | 20.34 µs | **24.8x** |
| 1,000 | 0.166 ms | 0.948 ms | **5.70x** | 280.1 ns | 5.28 µs | **18.9x** | 1.03 µs | 17.21 µs | **16.7x** |
| 10,000 | 2.06 ms | 15.19 ms | **7.37x** | 345.9 ns | 6.78 µs | **19.6x** | 1.16 µs | 20.57 µs | **17.8x** |
| 100,000 | 25.18 ms | 210.80 ms | **8.37x** | 478.6 ns | 9.50 µs | **19.9x** | 1.34 µs | 25.26 µs | **18.9x** |
| 1,000,000 | 306.85 ms | 4.62 s | **15.04x** | 1.33 µs | 15.50 µs | **11.7x** | 1.69 µs | 27.78 µs | **16.4x** |
### Detailed C++ KDTree Results

| Points ($N$) | Build Time | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|
| 100 | 0.021 ms | 212.0 ns | 820.6 ns | 4,715,926 qps | 1,218,692 qps |
| 1,000 | 0.166 ms | 280.1 ns | 1.03 µs | 3,570,574 qps | 972,491 qps |
| 10,000 | 2.06 ms | 345.9 ns | 1.16 µs | 2,891,189 qps | 862,936 qps |
| 100,000 | 25.18 ms | 478.6 ns | 1.34 µs | 2,089,510 qps | 747,599 qps |
| 1,000,000 | 306.85 ms | 1.33 µs | 1.69 µs | 754,275 qps | 590,782 qps |

### Detailed Pure Python KDTree Results

| Points ($N$) | Build Time | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|
| 100 | 0.095 ms | 3.92 µs | 20.34 µs | 255,215 qps | 49,170 qps |
| 1,000 | 0.948 ms | 5.28 µs | 17.21 µs | 189,357 qps | 58,094 qps |
| 10,000 | 15.19 ms | 6.78 µs | 20.57 µs | 147,467 qps | 48,607 qps |
| 100,000 | 210.80 ms | 9.50 µs | 25.26 µs | 105,252 qps | 39,584 qps |
| 1,000,000 | 4.62 s | 15.50 µs | 27.78 µs | 64,532 qps | 36,002 qps |


## GeoHilbert Benchmarks (Latitude/Longitude)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.455 ms | 18.49 ms | **40.67x** | 426.1 ns | 22.57 µs | **53.0x** | 0.025 ms | 0.009 ms | **0.4x** |
| 10,000 | 4.46 ms | 183.60 ms | **41.12x** | 433.2 ns | 22.22 µs | **51.3x** | 0.186 ms | 0.026 ms | **0.1x** |
| 100,000 | 46.46 ms | 1.89 s | **40.61x** | 448.0 ns | 22.62 µs | **50.5x** | 2.05 ms | 0.632 ms | **0.3x** |
| 1,000,000 | 575.54 ms | 18.81 s | **32.69x** | 550.3 ns | 22.90 µs | **41.6x** | 19.94 ms | 15.95 ms | **0.8x** |

### Detailed C++ GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | `hilbert_order` | Nearest QPS |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.455 ms | 426.1 ns | 414.1 ns | 0.025 ms | 2,347,060 qps |
| 10,000 | 4.46 ms | 433.2 ns | 398.2 ns | 0.186 ms | 2,308,304 qps |
| 100,000 | 46.46 ms | 448.0 ns | 436.2 ns | 2.05 ms | 2,232,127 qps |
| 1,000,000 | 575.54 ms | 550.3 ns | 709.1 ns | 19.94 ms | 1,817,207 qps |

### Detailed Pure Python GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | `hilbert_order` | Nearest QPS |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 18.49 ms | 22.57 µs | 22.42 µs | 0.009 ms | 44,304 qps |
| 10,000 | 183.60 ms | 22.22 µs | 22.20 µs | 0.026 ms | 45,013 qps |
| 100,000 | 1.89 s | 22.62 µs | 23.40 µs | 0.632 ms | 44,212 qps |
| 1,000,000 | 18.81 s | 22.90 µs | 25.53 µs | 15.95 ms | 43,677 qps |


## Hilbert Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.413 ms | 11.34 ms | **27.46x** | 418.5 ns | 14.39 µs | **34.4x** | 0.023 ms | 0.008 ms | **0.3x** |
| 10,000 | 3.97 ms | 112.83 ms | **28.43x** | 429.7 ns | 14.34 µs | **33.4x** | 0.232 ms | 0.031 ms | **0.1x** |
| 100,000 | 42.45 ms | 1.13 s | **26.63x** | 432.7 ns | 14.53 µs | **33.6x** | 2.09 ms | 0.516 ms | **0.2x** |
| 1,000,000 | 522.02 ms | 11.57 s | **22.15x** | 653.1 ns | 14.60 µs | **22.4x** | 31.08 ms | 14.76 ms | **0.5x** |

### Detailed C++ Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | `hilbert_order` | Nearest QPS |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.413 ms | 418.5 ns | 362.6 ns | 0.023 ms | 2,389,585 qps |
| 10,000 | 3.97 ms | 429.7 ns | 367.4 ns | 0.232 ms | 2,327,161 qps |
| 100,000 | 42.45 ms | 432.7 ns | 402.2 ns | 2.09 ms | 2,311,048 qps |
| 1,000,000 | 522.02 ms | 653.1 ns | 601.7 ns | 31.08 ms | 1,531,053 qps |

### Detailed Pure Python Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | `hilbert_order` | Nearest QPS |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 11.34 ms | 14.39 µs | 14.33 µs | 0.008 ms | 69,476 qps |
| 10,000 | 112.83 ms | 14.34 µs | 14.41 µs | 0.031 ms | 69,744 qps |
| 100,000 | 1.13 s | 14.53 µs | 15.04 µs | 0.516 ms | 68,827 qps |
| 1,000,000 | 11.57 s | 14.60 µs | 17.59 µs | 14.76 ms | 68,501 qps |


## Methodology

1. **Data**: Coordinates randomly and uniformly distributed over valid ranges ($[-90, 90]$ latitude, $[-180, 180]$ longitude for GeoKDTree and GeoHilbert; $[0, 1000] \times [0, 1000]$ for 2D KDTree and Hilbert).
2. **Timing**: Measured with `time.perf_counter()` over thousands of repeated lookups to compute stable averages.
3. **Reproducibility**: Run `uv run python utils/benchmark.py` to regenerate these benchmarks on your hardware.
