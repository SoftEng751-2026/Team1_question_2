#include <iostream>
#include <vector>
#include <cmath>
#include <chrono>
#include <omp.h>

class HeatStencil {
public:
    int N;
    int iterations;
    std::vector<double> u;
    std::vector<double> uNew;

    HeatStencil(int N, int iterations)
        : N(N), iterations(iterations), u(N * N), uNew(N * N) {
        initGrid();
    }

    // Initialize grid: boundary = 1.0, interior = 0.0
    void initGrid() {
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                int idx = i * N + j;
                if (i == 0 || i == N - 1 || j == 0 || j == N - 1) {
                    u[idx] = 1.0;
                } else {
                    u[idx] = 0.0;
                }
            }
        }
    }

    // Copy boundary values (fixed boundary)
    void copyBoundary() {
        for (int j = 0; j < N; j++) {
            uNew[j] = u[j];
            uNew[(N - 1) * N + j] = u[(N - 1) * N + j];
        }
        for (int i = 0; i < N; i++) {
            uNew[i * N] = u[i * N];
            uNew[i * N + (N - 1)] = u[i * N + (N - 1)];
        }
    }

    // Swap u and uNew
    void swapArrays() {
        std::swap(u, uNew);
    }

    // Sequential stencil update
    void stepSequential() {
        for (int i = 1; i < N - 1; i++) {
            for (int j = 1; j < N - 1; j++) {
                int idx = i * N + j;
                double up = u[idx - N];
                double down = u[idx + N];
                double left = u[idx - 1];
                double right = u[idx + 1];
                uNew[idx] = 0.25 * (up + down + left + right);
            }
        }
        copyBoundary();
        swapArrays();
    }

    // Parallel stencil using OpenMP
    void stepParallel() {
        #pragma omp parallel for schedule(static)
        for (int i = 1; i < N - 1; i++) {
            for (int j = 1; j < N - 1; j++) {
                int idx = i * N + j;
                double up = u[idx - N];
                double down = u[idx + N];
                double left = u[idx - 1];
                double right = u[idx + 1];
                uNew[idx] = 0.25 * (up + down + left + right);
            }
        }
        copyBoundary();
        swapArrays();
    }

    // Compute checksum to avoid dead-code elimination
    double checksum() const {
        double sum = 0.0;
        for (double v : u) sum += v;
        return sum;
    }

    // Run sequential version and measure time
    long long runSequential() {
        initGrid();
        auto start = std::chrono::high_resolution_clock::now();
        for (int it = 0; it < iterations; it++) {
            stepSequential();
        }
        auto end = std::chrono::high_resolution_clock::now();
        return std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    }

    // Run OpenMP version and measure time
    long long runParallel() {
        initGrid();
        auto start = std::chrono::high_resolution_clock::now();
        for (int it = 0; it < iterations; it++) {
            stepParallel();
        }
        auto end = std::chrono::high_resolution_clock::now();
        return std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    }
};

int main(int argc, char** argv) {
    int N = 2048;
    int iterations = 200;
    int threads = omp_get_max_threads();

    if (argc >= 2) N = std::stoi(argv[1]);
    if (argc >= 3) iterations = std::stoi(argv[2]);
    if (argc >= 4) threads = std::stoi(argv[3]);

    omp_set_num_threads(threads);

    HeatStencil solver(N, iterations);

    // Warm-up
    solver.runSequential();
    solver.runParallel();

    long long tSeq = solver.runSequential();
    double sumSeq = solver.checksum();

    long long tPar = solver.runParallel();
    double sumPar = solver.checksum();

    std::cout << "Sequential: " << tSeq << " ms, checksum = " << sumSeq << "\n";
    std::cout << "OpenMP:     " << tPar << " ms, checksum = " << sumPar
              << ", speedup = " << (double)tSeq / tPar << "\n";
    
    std::cout << "Press Enter to exit...";
    std::cin.get();

    return 0;
}
