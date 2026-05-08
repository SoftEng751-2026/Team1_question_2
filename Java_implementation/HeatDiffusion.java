/*
 * Heat Diffusion Simulation (2D 5‑point stencil)
 *
 * This program simulates heat diffusion on a 2D grid using an explicit
 * finite‑difference method. Each cell is updated based on the values of
 * its four direct neighbours (up, down, left, right), forming the classic
 * 5‑point stencil approximation of the Laplacian operator.
 *
 * The simulation uses two grids (grid1 and grid2) to implement double
 * buffering. Each iteration reads from a source grid and writes updated
 * values into the destination grid. This prevents read–write conflicts,
 * ensuring that every new value is computed strictly from the previous
 * time step.
 *
 * After each iteration, the roles of the two grids are swapped. Depending
 * on whether the total number of steps is even or odd, the final state
 * will reside in either grid1 or grid2. The print method selects the
 * correct grid based on this flag.
 */

public class HeatDiffusion {
    private final int rows;
    private final int cols;
    private final double alpha;
    private double[][] grid1;
    private double[][] grid2;

    public HeatDiffusion(int rows, int cols, double alpha) {
        this.rows = rows;
        this.cols = cols;
        this.alpha = alpha;
        this.grid1 = new double[rows][cols];
        this.grid2 = new double[rows][cols];
    }

    /**
     * Set up an initial heat source in the middle of the grid.
     */
    public void initialize() {
        grid1[rows / 2][cols / 2] = 100.0;
    }

    /**
     * Performs one iteration of the heat diffusion stencil.
     * @param useGrid1AsSource toggle which buffer acts as input.
     */
    public void step(boolean useGrid1AsSource) {
        double[][] src = useGrid1AsSource ? grid1 : grid2;
        double[][] dst = useGrid1AsSource ? grid2 : grid1;

        for (int i = 1; i < rows - 1; i++) {
            for (int j = 1; j < cols - 1; j++) {
                dst[i][j] = src[i][j] + alpha * (
                    src[i + 1][j] + src[i - 1][j] +
                    src[i][j + 1] + src[i][j - 1] -
                    4.0 * src[i][j]
                );
            }
        }
    }

    public void printGrid(boolean fromGrid1) {
        double[][] grid = fromGrid1 ? grid1 : grid2;
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                System.out.printf("%6.2f ", grid[i][j]);
            }
            System.out.println();
        }
    }

    public static void main(String[] args) {
        int size = 10;
        int steps = 5;
        double alpha = 0.2;

        HeatDiffusion solver = new HeatDiffusion(size, size, alpha);
        solver.initialize();

        boolean currentIsGrid1 = true;
        for (int t = 0; t < steps; t++) {
            solver.step(currentIsGrid1);
            currentIsGrid1 = !currentIsGrid1;
        }

        System.out.println("Final state after " + steps + " steps:");
        solver.printGrid(currentIsGrid1);
    }
}
