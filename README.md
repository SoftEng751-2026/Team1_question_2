# Parallel Stencil Computations: Java ForkJoin vs C++ OpenMP

Stencil computations are a fundamental pattern in high-performance computing (HPC), used to numerically solve partial differential equations (PDEs) across structured grids. They iteratively update grid points based on values from neighbouring points using a fixed pattern, known as a stencil.

This project implements and benchmarks two stencil algorithms in **Java** (ForkJoin) and **C++** (OpenMP), comparing shared-memory parallelism and memory (cache) optimisation strategies across both languages. More detailed analysis is included in the report.

---

## Algorithms

### 1. Conway's Game of Life (9-point stencil)
A cellular automaton where each cell's next state depends on its 8 neighbours. Discrete integer grid, logic-heavy per-cell computation.

- **Sequential baseline**: 2D `vector<vector<int>>` (C++) / `int[][]` (Java)
- **Optimised parallel**: Flat 1D arrays with cache-line padding, loop tiling (64×64), OpenMP `schedule(static)` (C++) / ForkJoin recursive splitting (Java)

### 2. Heat Diffusion (5-point stencil)
An explicit finite-difference approximation of the heat equation. Each cell is updated based on its 4 direct neighbours using a constant thermal diffusivity (alpha = 0.1). Floating-point grid, compute-heavy.

- **Sequential baseline**: Flat `std::vector<double>` / `double[]` with loop tiling (32×32)
- **Optimised parallel**: Same tiled stencil with OpenMP `schedule(static)` + `#pragma omp simd` (C++) / ForkJoin `RecursiveAction` with row splitting (Java)

---

## Optimisation Techniques

| Technique | Benefit |
|-----------|---------|
| **Flat 1D arrays** | Eliminates pointer-chasing of nested vectors; sequential memory access enables hardware prefetching |
| **Cache-line padding** | Row stride padded to 64-byte boundary to prevent false sharing between threads |
| **Loop tiling (blocking)** | Processes grid in 32×32 or 64×64 tiles that fit in L1/L2 cache, reducing main memory traffic |
| **Double buffering** | Swaps grid references each iteration instead of copying (O(1) per timestep) |
| **SIMD vectorisation** | `#pragma omp simd` hints the compiler to generate AVX/SSE instructions for the inner loop |
| **Work stealing (ForkJoin)** | Java's recursive task decomposition adapts to load imbalance and NUMA topology |
| **Static scheduling (OpenMP)** | Optimal for regular stencils where every cell does identical work; zero dynamic overhead |

---

## Benchmark Configuration

Test cases defined in `tests_configs.csv` (5 grid sizes × 4 thread counts = 20 configs):

| Grid | Iterations | Seed | Threads |
|------|-----------|------|---------|
| 512×512 | 100 | 12345 | 1, 2, 4, 8 |
| 1024×1024 | 50 | 67890 | 1, 2, 4, 8 |
| 2048×2048 | 25 | 11111 | 1, 2, 4, 8 |
| 4096×4096 | 10 | 33333 | 1, 2, 4, 8 |
| 8192×8192 | 5 | 44444 | 1, 2, 4, 8 |

Iterations scale inversely with grid area to keep total work comparable. Each config is run **5 times** for statistical significance (mean ± std dev).

---



## Requirements

- **Java**: JDK 11+
- **C++**: GCC/G++ with OpenMP support
- **Python**: 3.10+ with `pandas` and `matplotlib`
- **Platform**: Linux / WSL recommended

---

## Usage

### Run benchmarks
```bash
# Game of Life
./run_tests.sh

# Heat Diffusion
./run_tests_heat_diffusion.sh
```

### Run analysis plots only
```bash
python create_analysis_plots.py
```

### Docker
```bash
docker build -t stencil_benchmark .
docker run --rm -v "%cd%":/app stencil_benchmark   # Windows
docker run --rm -v $(pwd):/app stencil_benchmark    # WSL/Mac
```

---

## Project Structure

```
├── run_tests.sh                          # Game of Life benchmark script
├── run_tests_heat_diffusion.sh           # Heat Diffusion benchmark script
├── tests_configs.csv                     # Test parameter matrix
├── create_analysis_plots.py              # Speedup, efficiency, ratio, throughput plots
│
├── Cpp_implementation/
│   ├── Cpp_fork_optimized.cpp            # GoL: OpenMP + cache-line padding
│   ├── Cpp_sequential.cpp                # GoL: sequential (vector-of-vectors)
│   ├── Heat_diffusion_benchmark.cpp      # Heat: serial + OpenMP
│   └── heat_diffusion.cpp                # Standalone heat diffusion
│
├── Java_implementation/
│   ├── Game_of_life_fork_optimized.java  # GoL: ForkJoin + cache-line padding
│   ├── Sequential_test.java              # GoL: sequential 
│   ├── Heat_diffusion_benchmark.java     # Heat: serial + ForkJoin 
│   ├── HeatDiffusion.java                # Standalone heat diffusion
│   └── TestCase.java                     # Shared parameter 
│
├── benchmark_results/
│   ├── perf_raw/
│   │   ├── all_results.csv               # GoL raw results (5 runs per config)
│   │   └── heat_diffusion_results.csv    # Heat raw results (5 runs per config)
│   └── benchmark_plots/                  # Generated plots 
│
└── Dockerfile
```
