#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <chrono>
#include <omp.h>

/**
 * Heat Diffusion Stencil Computation (C++ OpenMP Version)
 * Computes the distribution of heat over time in a 2D space.
 */
void run_heat_diffusion_parallel(int rows, int cols, int iterations, int seed, int threads) {
    // Optimization: Using a 1D vector instead of a 2D array/vector-of-vectors.
    // This ensures spatial locality as all elements are contiguous in memory,
    // allowing the hardware prefetcher to work efficiently and reducing cache misses.
    size_t size = (size_t)rows * cols;
    std::vector<double> current(size, 0.0);
    std::vector<double> next(size, 0.0);

    // The alpha (thermal diffusivity) constant. 
    // For stability in a 2D explicit finite difference scheme, the Courant-Friedrichs-Lewy 
    // condition requires alpha * dt / (dx^2) <= 0.25. Since dx and dt are assumed to be 1,
    // alpha = 0.1 ensures the simulation remains numerically stable.
    const double alpha = 0.1; 

    // Cache Optimization: Loop Tiling (Blocking).
    // Modern CPUs have limited L1/L2 cache. Processing the grid in 32x32 blocks 
    // (approx 8KB per block for doubles) ensures the data stays in cache during
    // the stencil update, reducing the "Memory Wall" bottleneck.
    const int TILE_SIZE = 32; 

    // Initialization: Place a concentrated heat source in the center.
    current[(rows / 2) * cols + (cols / 2)] = (double)seed * 10.0;

    auto start = std::chrono::high_resolution_clock::now();

    for (int t = 0; t < iterations; ++t) {
        // Shared Memory Parallelism Choice: schedule(static)
        // Reasoning: In a stencil computation, every cell requires the same number of 
        // floating-point operations. Workload is perfectly balanced across the grid.
        // 'static' scheduling divides iterations into equal chunks at the start, 
        // which eliminates the overhead of a centralized task queue required by 
        // 'dynamic' or 'guided' scheduling, making it the most efficient choice 
        // for uniform structured grids.
        #pragma omp parallel for num_threads(threads) schedule(static)
        for (int ii = 1; ii < rows - 1; ii += TILE_SIZE) {
            for (int jj = 1; jj < cols - 1; jj += TILE_SIZE) {
                // Process a small tile that fits in cache
                for (int i = ii; i < std::min(ii + TILE_SIZE, rows - 1); ++i) {
                    int row_offset = i * cols;
                    int next_row = (i + 1) * cols;
                    int prev_row = (i - 1) * cols;
                    
                    // SIMD (Single Instruction Multiple Data) Optimization.
                    // Hints the compiler to vectorize the inner loop using 
                    // AVX/SSE registers to process multiple pixels in one clock cycle.
                    #pragma omp simd 
                    for (int j = jj; j < std::min(jj + TILE_SIZE, cols - 1); ++j) {
                        int idx = row_offset + j;
                        // 5-point stencil: Update based on self and 4 neighbors.
                        next[idx] = current[idx] + alpha * (
                            current[next_row + j] +
                            current[prev_row + j] +
                            current[idx + 1] +
                            current[idx - 1] -
                            4.0 * current[idx]
                        );
                    }
                }
            }
        }
        // Swap buffer references (using swap on vectors is O(1))
        current.swap(next);
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();

    // Output result line for performance tracking
    std::cout << "HeatDiffusion_Cpp_OMP," << rows << "," << cols << "," 
              << iterations << "," << seed << "," << threads << "," << duration << std::endl;
}

/**
 * Heat Diffusion Stencil Computation (C++ Sequential Version)
 * Same algorithm and cache optimizations, but no OpenMP.
 */
void run_heat_diffusion_sequential(int rows, int cols, int iterations, int seed, int threads) {
    // We maintain tiling in the sequential version to provide a fair baseline
    // comparing only the effect of multi-threading, not the cache optimization itself.
    size_t size = (size_t)rows * cols;
    std::vector<double> current(size, 0.0);
    std::vector<double> next(size, 0.0);
    const double alpha = 0.1;
    const int TILE_SIZE = 32;

    current[(rows / 2) * cols + (cols / 2)] = (double)seed * 10.0;

    auto start = std::chrono::high_resolution_clock::now();

    for (int t = 0; t < iterations; ++t) {
        for (int ii = 1; ii < rows - 1; ii += TILE_SIZE) {
            for (int jj = 1; jj < cols - 1; jj += TILE_SIZE) {
                for (int i = ii; i < std::min(ii + TILE_SIZE, rows - 1); ++i) {
                    int row_offset = i * cols;
                    int next_row = (i + 1) * cols;
                    int prev_row = (i - 1) * cols;
                    for (int j = jj; j < std::min(jj + TILE_SIZE, cols - 1); ++j) {
                        int idx = row_offset + j;
                        next[idx] = current[idx] + alpha * (
                            current[next_row + j] + 
                            current[prev_row + j] +
                            current[idx + 1] + 
                            current[idx - 1] - 
                            4.0 * current[idx]);
                    }
                }
            }
        }
        current.swap(next);
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    std::cout << "HeatDiffusion_Cpp_Sequential," << rows << "," << cols << "," 
              << iterations << "," << seed << "," << threads << "," << duration << std::endl;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <config_csv>" << std::endl;
        return 1;
    }

    std::ifstream file(argv[1]);
    if (!file.is_open()) return 1;

    std::string line;
    // CSV Header for standard output
    std::cout << "implementation,rows,cols,iterations,seed,threads,time_ms" << std::endl;

    std::getline(file, line); // Skip config header
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string item;
        std::vector<int> p;
        while (std::getline(ss, item, ',')) {
            try {
                p.push_back(std::stoi(item));
            } catch (...) { continue; }
        }

        if (p.size() >= 5) {
            run_heat_diffusion_sequential(p[0], p[1], p[2], p[3], p[4]);
            run_heat_diffusion_parallel(p[0], p[1], p[2], p[3], p[4]);
        }
    }

    return 0;
}