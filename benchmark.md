# GeoKDTree Performance Benchmarks

Automated performance benchmarks for `geokdtree` comparing C++ and Pure Python implementations across various dataset scales.

## Environment

| Attribute | Value |
|---|---|
| **Date** | 2026-11-05 21:45:11 UTC |
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
| 1,000 | 0.335 ms | 1.33 ms | **3.98x** | 292.7 ns | 7.57 µs | **25.9x** | 1.48 µs | 50.42 µs | **34.0x** |
| 10,000 | 4.43 ms | 17.03 ms | **3.84x** | 407.5 ns | 9.77 µs | **24.0x** | 2.02 µs | 84.08 µs | **41.5x** |
| 100,000 | 47.75 ms | 280.05 ms | **5.86x** | 747.7 ns | 15.41 µs | **20.6x** | 3.18 µs | 228.39 µs | **71.9x** |
| 1,000,000 | 555.81 ms | 5.42 s | **9.76x** | 1.40 µs | 24.01 µs | **17.2x** | 7.88 µs | 614.95 µs | **78.1x** |

### Detailed C++ GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.335 ms | 292.7 ns | 313.2 ns | 1.48 µs | 3,416,808 qps | 675,064 qps |
| 10,000 | 4.43 ms | 407.5 ns | 438.5 ns | 2.02 µs | 2,454,076 qps | 493,941 qps |
| 100,000 | 47.75 ms | 747.7 ns | 622.9 ns | 3.18 µs | 1,337,377 qps | 314,646 qps |
| 1,000,000 | 555.81 ms | 1.40 µs | 768.5 ns | 7.88 µs | 714,865 qps | 126,955 qps |

### Detailed Pure Python GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1.33 ms | 7.57 µs | 7.73 µs | 50.42 µs | 132,044 qps | 19,831 qps |
| 10,000 | 17.03 ms | 9.77 µs | 9.88 µs | 84.08 µs | 102,387 qps | 11,893 qps |
| 100,000 | 280.05 ms | 15.41 µs | 14.02 µs | 228.39 µs | 64,894 qps | 4,378 qps |
| 1,000,000 | 5.42 s | 24.01 µs | 21.51 µs | 614.95 µs | 41,652 qps | 1,626 qps |


## KDTree Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.021 ms | 0.098 ms | **4.56x** | 211.5 ns | 5.73 µs | **27.1x** | 821.1 ns | 20.46 µs | **24.9x** |
| 1,000 | 0.167 ms | 0.969 ms | **5.81x** | 284.4 ns | 7.82 µs | **27.5x** | 1.04 µs | 17.53 µs | **16.9x** |
| 10,000 | 2.05 ms | 15.74 ms | **7.70x** | 365.9 ns | 10.40 µs | **28.4x** | 1.22 µs | 21.63 µs | **17.7x** |
| 100,000 | 24.51 ms | 228.71 ms | **9.33x** | 620.7 ns | 13.85 µs | **22.3x** | 1.46 µs | 28.37 µs | **19.4x** |
| 1,000,000 | 306.07 ms | 5.12 s | **16.73x** | 1.21 µs | 19.73 µs | **16.3x** | 1.74 µs | 28.26 µs | **16.2x** |
### Detailed C++ KDTree Results

| Points ($N$) | Build Time | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|
| 100 | 0.021 ms | 211.5 ns | 821.1 ns | 4,727,850 qps | 1,217,890 qps |
| 1,000 | 0.167 ms | 284.4 ns | 1.04 µs | 3,515,563 qps | 963,814 qps |
| 10,000 | 2.05 ms | 365.9 ns | 1.22 µs | 2,733,239 qps | 817,934 qps |
| 100,000 | 24.51 ms | 620.7 ns | 1.46 µs | 1,611,136 qps | 683,961 qps |
| 1,000,000 | 306.07 ms | 1.21 µs | 1.74 µs | 828,126 qps | 573,453 qps |

### Detailed Pure Python KDTree Results

| Points ($N$) | Build Time | `closest_point` | `closest_point_per_quadrant` | Nearest QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|
| 100 | 0.098 ms | 5.73 µs | 20.46 µs | 174,418 qps | 48,880 qps |
| 1,000 | 0.969 ms | 7.82 µs | 17.53 µs | 127,873 qps | 57,037 qps |
| 10,000 | 15.74 ms | 10.40 µs | 21.63 µs | 96,148 qps | 46,221 qps |
| 100,000 | 228.71 ms | 13.85 µs | 28.37 µs | 72,193 qps | 35,245 qps |
| 1,000,000 | 5.12 s | 19.73 µs | 28.26 µs | 50,687 qps | 35,382 qps |


## GeoHilbert Benchmarks (Latitude/Longitude)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.465 ms | 18.73 ms | **40.27x** | 428.6 ns | 23.21 µs | **54.2x** | 0.030 ms | 0.010 ms | **0.3x** |
| 10,000 | 4.56 ms | 193.41 ms | **42.39x** | 441.1 ns | 24.02 µs | **54.5x** | 0.259 ms | 0.107 ms | **0.4x** |
| 100,000 | 48.45 ms | 1.88 s | **38.87x** | 480.0 ns | 25.91 µs | **54.0x** | 2.72 ms | 0.742 ms | **0.3x** |
| 1,000,000 | 605.60 ms | 19.39 s | **32.01x** | 598.9 ns | 24.13 µs | **40.3x** | 22.20 ms | 14.89 ms | **0.7x** |

### Detailed C++ GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | `hilbert_order` | Nearest QPS |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.465 ms | 428.6 ns | 456.6 ns | 0.030 ms | 2,333,420 qps |
| 10,000 | 4.56 ms | 441.1 ns | 461.3 ns | 0.259 ms | 2,267,156 qps |
| 100,000 | 48.45 ms | 480.0 ns | 440.9 ns | 2.72 ms | 2,083,146 qps |
| 1,000,000 | 605.60 ms | 598.9 ns | 657.8 ns | 22.20 ms | 1,669,755 qps |

### Detailed Pure Python GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | `hilbert_order` | Nearest QPS |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 18.73 ms | 23.21 µs | 23.08 µs | 0.010 ms | 43,086 qps |
| 10,000 | 193.41 ms | 24.02 µs | 22.94 µs | 0.107 ms | 41,632 qps |
| 100,000 | 1.88 s | 25.91 µs | 30.26 µs | 0.742 ms | 38,598 qps |
| 1,000,000 | 19.39 s | 24.13 µs | 26.82 µs | 14.89 ms | 41,450 qps |


## Hilbert Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.408 ms | 11.55 ms | **28.31x** | 461.8 ns | 15.14 µs | **32.8x** | 0.031 ms | 0.011 ms | **0.3x** |
| 10,000 | 4.11 ms | 116.42 ms | **28.36x** | 476.5 ns | 15.14 µs | **31.8x** | 0.294 ms | 0.060 ms | **0.2x** |
| 100,000 | 43.73 ms | 1.18 s | **27.06x** | 495.6 ns | 15.61 µs | **31.5x** | 2.51 ms | 1.08 ms | **0.4x** |
| 1,000,000 | 541.87 ms | 11.99 s | **22.12x** | 730.0 ns | 15.00 µs | **20.5x** | 31.60 ms | 15.59 ms | **0.5x** |

### Detailed C++ Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | `hilbert_order` | Nearest QPS |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.408 ms | 461.8 ns | 391.4 ns | 0.031 ms | 2,165,549 qps |
| 10,000 | 4.11 ms | 476.5 ns | 385.1 ns | 0.294 ms | 2,098,827 qps |
| 100,000 | 43.73 ms | 495.6 ns | 406.3 ns | 2.51 ms | 2,017,621 qps |
| 1,000,000 | 541.87 ms | 730.0 ns | 615.4 ns | 31.60 ms | 1,369,788 qps |

### Detailed Pure Python Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | `hilbert_order` | Nearest QPS |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 11.55 ms | 15.14 µs | 14.56 µs | 0.011 ms | 66,064 qps |
| 10,000 | 116.42 ms | 15.14 µs | 14.96 µs | 0.060 ms | 66,060 qps |
| 100,000 | 1.18 s | 15.61 µs | 15.43 µs | 1.08 ms | 64,077 qps |
| 1,000,000 | 11.99 s | 15.00 µs | 17.87 µs | 15.59 ms | 66,657 qps |


## Methodology

1. **Data**: Coordinates randomly and uniformly distributed over valid ranges ($[-90, 90]$ latitude, $[-180, 180]$ longitude for GeoKDTree and GeoHilbert; $[0, 1000] \times [0, 1000]$ for 2D KDTree and Hilbert).
2. **Timing**: Measured with `time.perf_counter()` over thousands of repeated lookups to compute stable averages.
3. **Reproducibility**: Run `uv run python utils/benchmark.py` to regenerate these benchmarks on your hardware.
