#include <iostream>
#include <vector>
#include <chrono>
#include <string>

/**
 * 1D vector VS 2D array/vector-of-vectors tests:
 * 1. 1D Flattened Vector
 * 2. 2D Vector of Vectors
 */

const double ALPHA = 0.1;

void run_1d_benchmark(int N, int iterations) {
    std::vector<double> current(N * N, 0.0);
    std::vector<double> next(N * N, 0.0);
    
    current[(N / 2) * N + (N / 2)] = 1000.0;

    auto start = std::chrono::high_resolution_clock::now();

    for (int t = 0; t < iterations; ++t) {
        for (int i = 1; i < N - 1; ++i) {
            int row = i * N;
            int prev = (i - 1) * N;
            int next_r = (i + 1) * N;
            for (int j = 1; j < N - 1; ++j) {
                next[row + j] = current[row + j] + ALPHA * (
                    current[next_r + j] + current[prev + j] +
                    current[row + j + 1] + current[row + j - 1] - 4.0 * current[row + j]
                );
            }
        }
        current.swap(next);
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    std::cout << "FINAL_1D_TIME: " << ms << std::endl;
}

void run_2d_benchmark(int N, int iterations) {
    std::vector<std::vector<double>> current(N, std::vector<double>(N, 0.0));
    std::vector<std::vector<double>> next(N, std::vector<double>(N, 0.0));
    
    current[N / 2][N / 2] = 1000.0;

    auto start = std::chrono::high_resolution_clock::now();

    for (int t = 0; t < iterations; ++t) {
        for (int i = 1; i < N - 1; ++i) {
            for (int j = 1; j < N - 1; ++j) {
                next[i][j] = current[i][j] + ALPHA * (
                    current[i + 1][j] + current[i - 1][j] +
                    current[i][j + 1] + current[i][j - 1] - 4.0 * current[i][j]
                );
            }
        }
        current.swap(next); 
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    std::cout << "FINAL_2D_TIME: " << ms << std::endl;
}

int main(int argc, char* argv[]) {
    int N = 1024;
    int iterations = 2500;

    if (argc >= 2) N = std::stoi(argv[1]);
    if (argc >= 3) iterations = std::stoi(argv[2]);

    std::cout << "Grid: " << N << "x" << N << ", Iterations: " << iterations << "\n";
    
    run_1d_benchmark(N, iterations);
    run_2d_benchmark(N, iterations);

    return 0;
}