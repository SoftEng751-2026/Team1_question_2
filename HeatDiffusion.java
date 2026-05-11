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

import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveAction;

public class HeatDiffusion {
    private final int rows;
    private final int cols;
    private final double alpha;
    private double[][] grid1;
    private double[][] grid2;
    private final ForkJoinPool pool;

    public HeatDiffusion(int rows, int cols, double alpha) {
        this.rows = rows;
        this.cols = cols;
        this.alpha = alpha;
        this.grid1 = new double[rows][cols];
        this.grid2 = new double[rows][cols];
        this.pool = new ForkJoinPool(); // Shared memory thread pool
    }

    public void initialize() {
        grid1[rows / 2][cols / 2] = 100.0;
    }

    // Parallel Task Definition
    private class StencilTask extends RecursiveAction {
        private static final int THRESHOLD = 64; // Adjusted for cache-line efficiency
        private final int startRow, endRow;
        private final double[][] src, dst;

        StencilTask(int startRow, int endRow, double[][] src, double[][] dst) {
            this.startRow = startRow;
            this.endRow = endRow;
            this.src = src;
            this.dst = dst;
        }

        @Override
        protected void compute() {
            if (endRow - startRow <= THRESHOLD) {
                for (int i = startRow; i < endRow; i++) {
                    for (int j = 1; j < cols - 1; j++) {
                        dst[i][j] = src[i][j] + alpha * (
                            src[i + 1][j] + src[i - 1][j] +
                            src[i][j + 1] + src[i][j - 1] -
                            4.0 * src[i][j]
                        );
                    }
                }
            } else {
                int mid = (startRow + endRow) / 2;
                invokeAll(new StencilTask(startRow, mid, src, dst),
                          new StencilTask(mid, endRow, src, dst));
            }
        }
    }

    public void step(boolean useGrid1AsSource) {
        double[][] src = useGrid1AsSource ? grid1 : grid2;
        double[][] dst = useGrid1AsSource ? grid2 : grid1;
        pool.invoke(new StencilTask(1, rows - 1, src, dst));
    }

    public static void main(String[] args) {
        int size = 1000;
        int steps = 100;
        double alpha = 0.2;

        HeatDiffusion solver = new HeatDiffusion(size, size, alpha);
        solver.initialize();

        long startTime = System.currentTimeMillis();

        boolean currentIsGrid1 = true;
        for (int t = 0; t < steps; t++) {
            solver.step(currentIsGrid1);
            currentIsGrid1 = !currentIsGrid1;
        }

        long endTime = System.currentTimeMillis();

        System.out.println("Java Parallel Simulation Complete.");
        System.out.println("Grid: " + size + "x" + size + " | Steps: " + steps);
        System.out.println("Execution Time: " + (endTime - startTime) / 1000.0 + " seconds");
    }
}
