# GeoKDTree Performance Benchmarks

Automated performance benchmarks for `geokdtree` comparing C++ and Pure Python implementations across various dataset scales.

## Environment

| Attribute | Value |
|---|---|
| **Date** | 2026-11-20 21:13:08 UTC |
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
| 1,000 | 0.270 ms | 1.44 ms | **5.35x** | 282.5 ns | 7.84 µs | **27.8x** | 264.0 ns | 8.16 µs | **30.9x** | 1.47 µs | 50.57 µs | **34.5x** |
| 10,000 | 3.42 ms | 17.15 ms | **5.02x** | 368.3 ns | 9.99 µs | **27.1x** | 337.6 ns | 10.17 µs | **30.1x** | 1.82 µs | 79.90 µs | **43.8x** |
| 100,000 | 40.01 ms | 274.13 ms | **6.85x** | 700.3 ns | 16.25 µs | **23.2x** | 478.5 ns | 15.66 µs | **32.7x** | 2.96 µs | 208.42 µs | **70.4x** |
| 1,000,000 | 473.23 ms | 5.22 s | **11.03x** | 1.36 µs | 21.66 µs | **15.9x** | 705.7 ns | 14.32 µs | **20.3x** | 5.97 µs | 565.86 µs | **94.9x** |

### Detailed C++ GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | Batch (`closest_indices`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.270 ms | 282.5 ns | 306.8 ns | 264.0 ns | 1.47 µs | 3,539,652 qps | 3,788,392 qps | 682,337 qps |
| 10,000 | 3.42 ms | 368.3 ns | 399.5 ns | 337.6 ns | 1.82 µs | 2,715,514 qps | 2,962,223 qps | 548,115 qps |
| 100,000 | 40.01 ms | 700.3 ns | 587.3 ns | 478.5 ns | 2.96 µs | 1,428,059 qps | 2,089,864 qps | 337,829 qps |
| 1,000,000 | 473.23 ms | 1.36 µs | 749.3 ns | 705.7 ns | 5.97 µs | 736,114 qps | 1,417,042 qps | 167,641 qps |

### Detailed Pure Python GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` | `closest_point` | Batch (`closest_indices`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1.44 ms | 7.84 µs | 7.70 µs | 8.16 µs | 50.57 µs | 127,531 qps | 122,614 qps | 19,776 qps |
| 10,000 | 17.15 ms | 9.99 µs | 9.97 µs | 10.17 µs | 79.90 µs | 100,113 qps | 98,336 qps | 12,515 qps |
| 100,000 | 274.13 ms | 16.25 µs | 16.53 µs | 15.66 µs | 208.42 µs | 61,548 qps | 63,853 qps | 4,798 qps |
| 1,000,000 | 5.22 s | 21.66 µs | 14.50 µs | 14.32 µs | 565.86 µs | 46,168 qps | 69,817 qps | 1,767 qps |


## KDTree Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Batch | Python Batch | Batch Speedup | C++ 4-Quadrant | Python 4-Quadrant | Quadrant Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.019 ms | 0.109 ms | **5.72x** | 216.4 ns | 4.04 µs | **18.7x** | 238.8 ns | 4.26 µs | **17.8x** | 831.6 ns | 20.71 µs | **24.9x** |
| 1,000 | 0.157 ms | 1.07 ms | **6.81x** | 286.9 ns | 5.37 µs | **18.7x** | 314.5 ns | 5.69 µs | **18.1x** | 1.07 µs | 17.69 µs | **16.5x** |
| 10,000 | 1.78 ms | 15.54 ms | **8.73x** | 350.8 ns | 6.90 µs | **19.7x** | 364.8 ns | 7.11 µs | **19.5x** | 1.19 µs | 20.87 µs | **17.5x** |
| 100,000 | 21.73 ms | 221.17 ms | **10.18x** | 451.0 ns | 9.87 µs | **21.9x** | 423.0 ns | 9.76 µs | **23.1x** | 1.35 µs | 26.50 µs | **19.7x** |
| 1,000,000 | 267.68 ms | 4.78 s | **17.86x** | 1.26 µs | 15.16 µs | **12.0x** | 644.2 ns | 9.56 µs | **14.8x** | 1.68 µs | 27.96 µs | **16.7x** |
### Detailed C++ KDTree Results

| Points ($N$) | Build Time | `closest_point` | Batch (`closest_points`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.019 ms | 216.4 ns | 238.8 ns | 831.6 ns | 4,621,682 qps | 4,186,826 qps | 1,202,539 qps |
| 1,000 | 0.157 ms | 286.9 ns | 314.5 ns | 1.07 µs | 3,485,950 qps | 3,179,789 qps | 934,882 qps |
| 10,000 | 1.78 ms | 350.8 ns | 364.8 ns | 1.19 µs | 2,850,225 qps | 2,741,303 qps | 836,878 qps |
| 100,000 | 21.73 ms | 451.0 ns | 423.0 ns | 1.35 µs | 2,217,353 qps | 2,364,043 qps | 741,981 qps |
| 1,000,000 | 267.68 ms | 1.26 µs | 644.2 ns | 1.68 µs | 793,685 qps | 1,552,252 qps | 596,486 qps |

### Detailed Pure Python KDTree Results

| Points ($N$) | Build Time | `closest_point` | Batch (`closest_points`) | `closest_point_per_quadrant` | Nearest QPS | Batch QPS | Quadrant QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.109 ms | 4.04 µs | 4.26 µs | 20.71 µs | 247,648 qps | 234,705 qps | 48,291 qps |
| 1,000 | 1.07 ms | 5.37 µs | 5.69 µs | 17.69 µs | 186,259 qps | 175,784 qps | 56,536 qps |
| 10,000 | 15.54 ms | 6.90 µs | 7.11 µs | 20.87 µs | 144,926 qps | 140,585 qps | 47,906 qps |
| 100,000 | 221.17 ms | 9.87 µs | 9.76 µs | 26.50 µs | 101,314 qps | 102,428 qps | 37,728 qps |
| 1,000,000 | 4.78 s | 15.16 µs | 9.56 µs | 27.96 µs | 65,980 qps | 104,592 qps | 35,763 qps |


## GeoHilbert Benchmarks (Latitude/Longitude)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.433 ms | 18.83 ms | **43.48x** | 436.1 ns | 23.19 µs | **53.2x** | 0.025 ms | 0.009 ms | **0.4x** |
| 10,000 | 4.25 ms | 192.02 ms | **45.15x** | 453.5 ns | 23.47 µs | **51.7x** | 0.188 ms | 0.040 ms | **0.2x** |
| 100,000 | 44.27 ms | 1.91 s | **43.10x** | 590.2 ns | 24.20 µs | **41.0x** | 2.22 ms | 0.632 ms | **0.3x** |
| 1,000,000 | 461.31 ms | 19.51 s | **42.30x** | 659.2 ns | 24.07 µs | **36.5x** | 20.93 ms | 15.42 ms | **0.7x** |

### Detailed C++ GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.433 ms | 436.1 ns | 421.4 ns | 386.2 ns | 0.025 ms | 2,293,001 qps | 2,589,596 qps |
| 10,000 | 4.25 ms | 453.5 ns | 431.6 ns | 391.1 ns | 0.188 ms | 2,205,214 qps | 2,556,825 qps |
| 100,000 | 44.27 ms | 590.2 ns | 467.1 ns | 447.2 ns | 2.22 ms | 1,694,478 qps | 2,236,280 qps |
| 1,000,000 | 461.31 ms | 659.2 ns | 665.5 ns | 1.08 µs | 20.93 ms | 1,516,978 qps | 923,054 qps |

### Detailed Pure Python GeoHilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 18.83 ms | 23.19 µs | 23.22 µs | 23.42 µs | 0.009 ms | 43,122 qps | 42,696 qps |
| 10,000 | 192.02 ms | 23.47 µs | 23.69 µs | 23.78 µs | 0.040 ms | 42,615 qps | 42,049 qps |
| 100,000 | 1.91 s | 24.20 µs | 24.61 µs | 24.30 µs | 0.632 ms | 41,322 qps | 41,148 qps |
| 1,000,000 | 19.51 s | 24.07 µs | 26.48 µs | 23.81 µs | 15.42 ms | 41,541 qps | 41,992 qps |


## Hilbert Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build | Python Build | Build Speedup | C++ Nearest | Python Nearest | Nearest Speedup | C++ Order | Python Order | Order Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.415 ms | 11.62 ms | **28.03x** | 428.6 ns | 14.76 µs | **34.4x** | 0.022 ms | 0.009 ms | **0.4x** |
| 10,000 | 4.09 ms | 116.07 ms | **28.40x** | 450.1 ns | 14.98 µs | **33.3x** | 0.181 ms | 0.044 ms | **0.2x** |
| 100,000 | 40.14 ms | 1.16 s | **28.92x** | 469.7 ns | 14.77 µs | **31.4x** | 2.09 ms | 0.609 ms | **0.3x** |
| 1,000,000 | 484.50 ms | 11.90 s | **24.56x** | 729.8 ns | 14.85 µs | **20.3x** | 28.41 ms | 15.06 ms | **0.5x** |

### Detailed C++ Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.415 ms | 428.6 ns | 372.0 ns | 379.4 ns | 0.022 ms | 2,333,258 qps | 2,635,882 qps |
| 10,000 | 4.09 ms | 450.1 ns | 383.4 ns | 415.9 ns | 0.181 ms | 2,221,589 qps | 2,404,392 qps |
| 100,000 | 40.14 ms | 469.7 ns | 398.9 ns | 411.1 ns | 2.09 ms | 2,128,914 qps | 2,432,486 qps |
| 1,000,000 | 484.50 ms | 729.8 ns | 670.5 ns | 504.1 ns | 28.41 ms | 1,370,257 qps | 1,983,693 qps |

### Detailed Pure Python Hilbert Results

| Points ($N$) | Build Time | `closest_point` | `closest_idx` | Batch (`closest_indices`) | `hilbert_order` | Nearest QPS | Batch QPS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 11.62 ms | 14.76 µs | 14.96 µs | 14.78 µs | 0.009 ms | 67,753 qps | 67,661 qps |
| 10,000 | 116.07 ms | 14.98 µs | 15.27 µs | 15.19 µs | 0.044 ms | 66,744 qps | 65,827 qps |
| 100,000 | 1.16 s | 14.77 µs | 15.66 µs | 14.90 µs | 0.609 ms | 67,708 qps | 67,114 qps |
| 1,000,000 | 11.90 s | 14.85 µs | 17.94 µs | 15.13 µs | 15.06 ms | 67,360 qps | 66,074 qps |


## Methodology

1. **Data**: Coordinates randomly and uniformly distributed over valid ranges ($[-90, 90]$ latitude, $[-180, 180]$ longitude for GeoKDTree and GeoHilbert; $[0, 1000] \times [0, 1000]$ for 2D KDTree and Hilbert).
2. **Timing**: Measured with `time.perf_counter()` over thousands of repeated lookups to compute stable averages.
3. **Reproducibility**: Run `uv run python utils/benchmark.py` to regenerate these benchmarks on your hardware.
