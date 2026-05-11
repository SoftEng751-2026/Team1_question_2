/*
 * Heat Diffusion Simulation (2D 5‑point stencil)
 *
 * This program simulates heat diffusion on a 2D grid using an explicit
 * finite‑difference stencil. Each cell is updated based on the values of
 * its four neighbours (up, down, left, right), forming a classic 5‑point
 * stencil for approximating the Laplacian.
 *
 * The simulation uses two grids (grid1 and grid2) to implement
 * double buffering. Each iteration reads from a source grid and writes
 * results into the destination grid. This avoids read–write conflicts:
 * every new value must be computed strictly from the previous time step.
 *
 * After each iteration, the roles of the two grids are swapped. Depending
 * on whether the total number of steps is even or odd, the final state
 * will reside in either grid1 or grid2. The print function selects the
 * correct grid based on this flag.
 */

#include <iostream>
#include <vector>
#include <iomanip>
#include <omp.h> // Required for Parallelism

class HeatDiffusion {
private:
    int rows, cols;
    double alpha;
    std::vector<std::vector<double>> grid1;
    std::vector<std::vector<double>> grid2;

public:
    HeatDiffusion(int r, int c, double a) : rows(r), cols(c), alpha(a) {
        grid1.resize(rows, std::vector<double>(cols, 0.0));
        grid2.resize(rows, std::vector<double>(cols, 0.0));
    }

    void initialize() {
        grid1[rows / 2][cols / 2] = 100.0;
    }

    void step(bool useGrid1AsSource) {
        auto& src = useGrid1AsSource ? grid1 : grid2;
        auto& dst = useGrid1AsSource ? grid2 : grid1;

        // Parallelize the outer loop. Static scheduling is best for balanced stencils.
        #pragma omp parallel for schedule(static)
        for (int i = 1; i < rows - 1; ++i) {
            for (int j = 1; j < cols - 1; ++j) {
                dst[i][j] = src[i][j] + alpha * (
                    src[i + 1][j] + src[i - 1][j] +
                    src[i][j + 1] + src[i][j - 1] -
                    4.0 * src[i][j]
                );
            }
        }
    }

    void printGrid(bool fromGrid1) const {
        const auto& grid = fromGrid1 ? grid1 : grid2;
        for (int i = 0; i < rows; ++i) {
            for (int j = 0; j < cols; ++j) {
                std::cout << std::fixed << std::setprecision(2) << grid[i][j] << " ";
            }
            std::cout << "\n";
        }
    }
};

int main(int argc, char* argv[]) {
    int size = 1000; // Defaulting to large size for parallel testing
    int steps = 100;
    double alpha = 0.2;

    if (argc >= 2) size = std::stoi(argv[1]);
    if (argc >= 3) steps = std::stoi(argv[2]);

    double startTime = omp_get_wtime();

    HeatDiffusion solver(size, size, alpha);
    solver.initialize();

    bool currentIsGrid1 = true;
    for (int t = 0; t < steps; ++t) {
        solver.step(currentIsGrid1);
        currentIsGrid1 = !currentIsGrid1;
    }

    double endTime = omp_get_wtime();

    if (size <= 20) {
        solver.printGrid(currentIsGrid1);
    } else {
        std::cout << "C++ Parallel Simulation Complete." << std::endl;
        std::cout << "Grid: " << size << "x" << size << " | Steps: " << steps << std::endl;
        std::cout << "Execution Time: " << (endTime - startTime) << " seconds" << std::endl;
    }

    return 0;
}
