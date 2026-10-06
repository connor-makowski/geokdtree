# GeoKDTree Performance Benchmarks

Automated performance benchmarks for `geokdtree` comparing C++ and Pure Python implementations across various dataset scales.

## Environment

| Attribute | Value |
|---|---|
| **Date** | 2026-10-06 15:33:52 UTC |
| **OS** | Linux-7.0.0-38-generic-x86_64-with-glibc2.39 |
| **Architecture** | x86_64 |
| **Python** | CPython 3.14.5 |
| **C++ Acceleration** | Enabled (`nanobind`) |

## Executive Summary

- **Lookups in Microseconds / Nanoseconds**: Nearest-neighbor queries scale logarithmically ($O(\log N)$), completing in single-digit microseconds even with 1,000,000 coordinates.
- **C++ Speedup**: The compiled C++ extension delivers **~10x–20x faster nearest-neighbor lookups** and **1.4x–2x faster tree builds** compared to pure Python.
- **Scalable Tree Construction**: Tree construction scales at $O(N \log N)$, building a 100k spatial index in ~200–350 ms and a 1M spatial index in ~2.5–3.8 s.
- **Zero GIS Overhead**: Works directly with `(latitude, longitude)` coordinates using internal 3D spherical trigonometry Cartesian projections.

## GeoKDTree Benchmarks (Latitude/Longitude)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build Time | Python Build Time | Build Speedup | C++ Query Time | Python Query Time | Query Speedup | C++ Throughput |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1.06 ms | 1.75 ms | **1.65x** | 632.9 ns | 12.18 µs | **19.2x** | 1,580,078 ops/s |
| 10,000 | 14.77 ms | 21.12 ms | **1.43x** | 829.1 ns | 15.78 µs | **19.0x** | 1,206,105 ops/s |
| 100,000 | 220.25 ms | 331.71 ms | **1.51x** | 2.07 µs | 22.60 µs | **10.9x** | 482,492 ops/s |
| 1,000,000 | 3.57 s | 6.00 s | **1.68x** | 3.01 µs | 29.68 µs | **9.9x** | 332,239 ops/s |

### Detailed C++ GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` Query | `closest_point` Query | Throughput (QPS) |
|---:|---:|---:|---:|---:|
| 1,000 | 1.06 ms | 632.9 ns | 656.6 ns | 1,580,078 qps |
| 10,000 | 14.77 ms | 829.1 ns | 864.8 ns | 1,206,105 qps |
| 100,000 | 220.25 ms | 2.07 µs | 1.57 µs | 482,492 qps |
| 1,000,000 | 3.57 s | 3.01 µs | 1.34 µs | 332,239 qps |

### Detailed Pure Python GeoKDTree Results

| Points ($N$) | Build Time | `closest_idx` Query | `closest_point` Query | Throughput (QPS) |
|---:|---:|---:|---:|---:|
| 1,000 | 1.75 ms | 12.18 µs | 12.33 µs | 82,122 qps |
| 10,000 | 21.12 ms | 15.78 µs | 15.80 µs | 63,387 qps |
| 100,000 | 331.71 ms | 22.60 µs | 22.22 µs | 44,253 qps |
| 1,000,000 | 6.00 s | 29.68 µs | 22.89 µs | 33,695 qps |


## KDTree Benchmarks (Cartesian 2D)

### C++ vs Pure Python Comparison

| Dataset Size ($N$) | C++ Build Time | Python Build Time | Build Speedup | C++ Query Time | Python Query Time | Query Speedup | C++ Throughput |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.064 ms | 0.113 ms | **1.77x** | 432.7 ns | 7.46 µs | **17.2x** | 2,310,903 ops/s |
| 1,000 | 0.850 ms | 1.26 ms | **1.48x** | 559.4 ns | 10.28 µs | **18.4x** | 1,787,487 ops/s |
| 10,000 | 12.98 ms | 17.71 ms | **1.36x** | 709.6 ns | 12.97 µs | **18.3x** | 1,409,300 ops/s |
| 100,000 | 196.27 ms | 268.88 ms | **1.37x** | 1.44 µs | 17.33 µs | **12.0x** | 693,306 ops/s |
| 1,000,000 | 3.23 s | 5.54 s | **1.71x** | 2.43 µs | 23.95 µs | **9.9x** | 411,875 ops/s |

### Detailed Pure Python KDTree Results

| Points ($N$) | Build Time | Query Time | Throughput (QPS) |
|---:|---:|---:|---:|
| 100 | 0.113 ms | 7.46 µs | 134,129 qps |
| 1,000 | 1.26 ms | 10.28 µs | 97,313 qps |
| 10,000 | 17.71 ms | 12.97 µs | 77,088 qps |
| 100,000 | 268.88 ms | 17.33 µs | 57,691 qps |
| 1,000,000 | 5.54 s | 23.95 µs | 41,758 qps |


## Methodology

1. **Data**: Coordinates randomly and uniformly distributed over valid ranges ($[-90, 90]$ latitude, $[-180, 180]$ longitude for GeoKDTree; $[0, 1000] \times [0, 1000]$ for 2D KDTree).
2. **Timing**: Measured with `time.perf_counter()` over thousands of repeated lookups to compute stable averages.
3. **Reproducibility**: Run `uv run python utils/benchmark.py` to regenerate these benchmarks on your hardware.
