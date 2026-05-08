#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <random>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <omp.h>

using namespace std;


static constexpr int CACHE_LINE   = 64;                       
static constexpr int INTS_PER_CL  = CACHE_LINE / sizeof(int); 

struct TestCase {
    int rows, cols, iterations, seed, threads;
};


static inline int paddedStride(int cols) {
    return ((cols + INTS_PER_CL - 1) / INTS_PER_CL) * INTS_PER_CL;
}


static int* alignedAlloc(size_t count) {
    size_t bytes = count * sizeof(int);
#ifdef _WIN32
    int* p = static_cast<int*>(_aligned_malloc(bytes, CACHE_LINE));
#else
    int* p = static_cast<int*>(aligned_alloc(CACHE_LINE, bytes));
#endif
    memset(p, 0, bytes);
    return p;
}

static void alignedFree(int* p) {
#ifdef _WIN32
    _aligned_free(p);
#else
    free(p);
#endif
}


static void findNextGen(const int* __restrict__ cur,
                        int*       __restrict__ nxt,
                        int m, int n, int stride) {
    #pragma omp parallel for schedule(static)
    for (int i = 0; i < m; i++) {
        const int rowOff = i * stride;
        const int above  = (i - 1) * stride;
        const int below  = (i + 1) * stride;
        const bool hasUp   = (i > 0);
        const bool hasDown = (i < m - 1);

        for (int j = 0; j < n; j++) {
            int live = 0;
            const bool hasLeft  = (j > 0);
            const bool hasRight = (j < n - 1);

            if (hasUp) {
                if (hasLeft  && cur[above + j - 1]) live++;
                               if (cur[above + j])     live++;
                if (hasRight && cur[above + j + 1]) live++;
            }
            if (hasLeft  && cur[rowOff + j - 1]) live++;
            if (hasRight && cur[rowOff + j + 1]) live++;
            if (hasDown) {
                if (hasLeft  && cur[below + j - 1]) live++;
                               if (cur[below + j])     live++;
                if (hasRight && cur[below + j + 1]) live++;
            }

            if (cur[rowOff + j] == 1) {
                nxt[rowOff + j] = (live == 2 || live == 3) ? 1 : 0;
            } else {
                nxt[rowOff + j] = (live == 3) ? 1 : 0;
            }
        }
    }
}

int* generateGrid(int rows, int cols, int stride, int seed) {
    mt19937 gen(seed);
    uniform_int_distribution<> dis(0, 1);
    int* grid = alignedAlloc(static_cast<size_t>(rows) * stride);
    for (int i = 0; i < rows; i++) {
        int off = i * stride;
        for (int j = 0; j < cols; j++) {
            grid[off + j] = dis(gen);
        }
    }
    return grid;
}

vector<TestCase> readTestConfigs(const string& filename) {
    vector<TestCase> testCases;
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "Error: Could not open file: " << filename << endl;
        return testCases;
    }

    string line;
    getline(file, line);

    while (getline(file, line)) {
        if (line.empty()) continue;
        stringstream ss(line);
        string val;
        vector<int> row;
        while (getline(ss, val, ',')) {
            row.push_back(stoi(val));
        }
        if (row.size() >= 4) {
            int threads = (row.size() >= 5) ? row[4] : omp_get_max_threads();
            testCases.push_back({row[0], row[1], row[2], row[3], threads});
        }
    }
    return testCases;
}

int main(int argc, char* argv[]) {
    string csvPath = (argc > 1) ? argv[1] : "tests_configs.csv";

    vector<TestCase> testCases = readTestConfigs(csvPath);
    if (testCases.empty()) return 1;

    cout << "implementation,rows,cols,iterations,seed,threads,time_ms" << endl;

    for (const auto& tc : testCases) {
        int stride = paddedStride(tc.cols);
        size_t totalCells = static_cast<size_t>(tc.rows) * stride;

        int* currentGrid = generateGrid(tc.rows, tc.cols, stride, tc.seed);
        int* nextGrid    = alignedAlloc(totalCells);

        omp_set_num_threads(tc.threads);

        findNextGen(currentGrid, nextGrid, tc.rows, tc.cols, stride);
        swap(currentGrid, nextGrid);

        auto start = chrono::steady_clock::now();

        for (int i = 0; i < tc.iterations; i++) {
            findNextGen(currentGrid, nextGrid, tc.rows, tc.cols, stride);
            swap(currentGrid, nextGrid);
        }

        auto end = chrono::steady_clock::now();
        chrono::duration<double, milli> duration = end - start;

        cout << "cpp_optimized," << tc.rows << "," << tc.cols << ","
             << tc.iterations << "," << tc.seed << "," << tc.threads
             << "," << duration.count() << endl;

        alignedFree(currentGrid);
        alignedFree(nextGrid);
    }

    return 0;
}
