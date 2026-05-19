#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <chrono>
#include <omp.h>
#include <algorithm>

/**
 * Heat Diffusion Stencil Computation (C++ OpenMP Version)
 * Computes the distribution of heat over time in a 2D space.
 */
void run_heat_diffusion_parallel(int rows, int cols, int iterations, int seed, int threads) {
    size_t size = (size_t)rows * cols;
    std::vector<double> current(size, 0.0);
    std::vector<double> next(size, 0.0);

    const double alpha = 0.1; 
    const int TILE_SIZE = 32; 

    current[(rows / 2) * cols + (cols / 2)] = (double)seed * 10.0;

    auto start = std::chrono::high_resolution_clock::now();

    for (int t = 0; t < iterations; ++t) {
        // Advanced Optimization: Extract raw pointers with __restrict__ keywords.
        // This explicitly informs the compiler that 'cur_ptr' and 'nxt_ptr' do not alias 
        // (overlap) in memory, allowing the compiler to aggressively store data in hardware 
        // registers without constantly reloading from cache.
        double* __restrict__ cur_ptr = current.data();
        double* __restrict__ nxt_ptr = next.data();

        #pragma omp parallel for num_threads(threads) schedule(static)
        for (int ii = 1; ii < rows - 1; ii += TILE_SIZE) {
            int i_end = std::min(ii + TILE_SIZE, rows - 1);
            for (int jj = 1; jj < cols - 1; jj += TILE_SIZE) {
                int j_end = std::min(jj + TILE_SIZE, cols - 1);

                for (int i = ii; i < i_end; ++i) {
                    int row_offset = i * cols;
                    int next_row = (i + 1) * cols;
                    int prev_row = (i - 1) * cols;
                    
                    // SIMD Optimization combined with restrict pointer hints
                    #pragma omp simd 
                    for (int j = jj; j < j_end; ++j) {
                        int idx = row_offset + j;
                        nxt_ptr[idx] = cur_ptr[idx] + alpha * (
                            cur_ptr[next_row + j] +
                            cur_ptr[prev_row + j] +
                            cur_ptr[idx + 1] +
                            cur_ptr[idx - 1] -
                            4.0 * cur_ptr[idx]
                        );
                    }
                }
            }
        }
        current.swap(next);
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();

    std::cout << "HeatDiffusion_Cpp_OMP," << rows << "," << cols << "," 
              << iterations << "," << seed << "," << threads << "," << duration << std::endl;
}

/**
 * Heat Diffusion Stencil Computation (C++ Sequential Version)
 */
void run_heat_diffusion_sequential(int rows, int cols, int iterations, int seed, int threads) {
    size_t size = (size_t)rows * cols;
    std::vector<double> current(size, 0.0);
    std::vector<double> next(size, 0.0);
    const double alpha = 0.1;
    const int TILE_SIZE = 32;

    current[(rows / 2) * cols + (cols / 2)] = (double)seed * 10.0;

    auto start = std::chrono::high_resolution_clock::now();

    for (int t = 0; t < iterations; ++t) {
        double* __restrict__ cur_ptr = current.data();
        double* __restrict__ nxt_ptr = next.data();

        for (int ii = 1; ii < rows - 1; ii += TILE_SIZE) {
            int i_end = std::min(ii + TILE_SIZE, rows - 1);
            for (int jj = 1; jj < cols - 1; jj += TILE_SIZE) {
                int j_end = std::min(jj + TILE_SIZE, cols - 1);

                for (int i = ii; i < i_end; ++i) {
                    int row_offset = i * cols;
                    int next_row = (i + 1) * cols;
                    int prev_row = (i - 1) * cols;
                    
                    // Optimization: Compiler hint for unrolling the sequential baseline loop
                    #pragma vec retain source
                    for (int j = jj; j < j_end; ++j) {
                        int idx = row_offset + j;
                        nxt_ptr[idx] = cur_ptr[idx] + alpha * (
                            cur_ptr[next_row + j] + 
                            cur_ptr[prev_row + j] +
                            cur_ptr[idx + 1] + 
                            cur_ptr[idx - 1] - 
                            4.0 * cur_ptr[idx]);
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
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <mode> <config_csv>" << std::endl;
        std::cerr << "  mode: sequential | parallel" << std::endl;
        return 1;
    }

    std::string mode = argv[1];
    std::ifstream file(argv[2]);
    if (!file.is_open()) return 1;

    std::string line;
    std::cout << "implementation,rows,cols,iterations,seed,threads,time_ms" << std::endl;

    std::getline(file, line); 
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
            if (mode == "parallel") {
                run_heat_diffusion_parallel(p[0], p[1], p[2], p[3], p[4]);
            } else {
                run_heat_diffusion_sequential(p[0], p[1], p[2], p[3], p[4]);
            }
        }
    }

    return 0;
}