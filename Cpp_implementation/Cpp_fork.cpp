#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <random>
#include <chrono>
#include <omp.h>
using namespace std;

struct TestCase {
    int rows;       
    int cols;
    int iterations;
    int seed;
};

void findNextGen(const vector<vector<int>>& current, vector<vector<int>>& next) {
    int m = current.size();
    int n = current[0].size();
    
    const int dr[] = {0, 0, 1, -1, 1, 1, -1, -1};
    const int dc[] = {1, -1, 0, 0, 1, -1, 1, -1};

    #pragma omp parallel for collapse(2) schedule(static)
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            int live = 0;
            for (int k = 0; k < 8; k++) {
                int r = i + dr[k];
                int c = j + dc[k];
                if (r >= 0 && r < m && c >= 0 && c < n && current[r][c] == 1) {
                    live++;
                }
            }

            if (current[i][j] == 1) {
                next[i][j] = (live == 2 || live == 3) ? 1 : 0;
            } else {
                next[i][j] = (live == 3) ? 1 : 0;
            }
        }
    }
}

vector<vector<int>> generateGrid(int rows, int cols, int seed) {
    mt19937 gen(seed);
    uniform_int_distribution<> dis(0, 1);
    vector<vector<int>> grid(rows, vector<int>(cols));
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            grid[i][j] = dis(gen); 
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
        if (row.size() == 4) {
            testCases.push_back({row[0], row[1], row[2], row[3]});
        }
    }
    return testCases;
}

int main(int argc, char* argv[]) {
   
    string csvPath = (argc > 1) ? argv[1] : "tests_configs.csv";

    vector<TestCase> testCases = readTestConfigs(csvPath);
    if (testCases.empty()) {
        return 1;
    }

    cout << "implementation,rows,cols,iterations,seed,time_ms" << endl;

    for (const auto& tc : testCases) {
        vector<vector<int>> currentGrid = generateGrid(tc.rows, tc.cols, tc.seed);
        vector<vector<int>> nextGrid(tc.rows, vector<int>(tc.cols));

        auto start = chrono::high_resolution_clock::now();

        for (int i = 0; i < tc.iterations; i++) {
            findNextGen(currentGrid, nextGrid);
            currentGrid.swap(nextGrid);
        }

        auto end = chrono::high_resolution_clock::now();
        chrono::duration<double, std::milli> duration = end - start;

        cout << "cpp_fork," << tc.rows << "," << tc.cols << "," 
             << tc.iterations << "," << tc.seed << "," << duration.count() << endl;
    }

    return 0;
}