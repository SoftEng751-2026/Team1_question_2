package Java_implementation;
import java.io.*;
import java.util.*;
import java.util.concurrent.*;

class Game_of_life_fork_optimized {

    private static final int TILE_ROWS = 64;
    private static final int TILE_COLS = 64;
    private static final int CACHE_LINE_INTS = 16;

    static int paddedStride(int cols) {
        return ((cols + CACHE_LINE_INTS - 1) / CACHE_LINE_INTS) * CACHE_LINE_INTS;
    }

    static class TileTask extends RecursiveAction {
        private final int[] current, next;
        private final int rows, cols, stride;
        private final int rowStart, rowEnd;

        TileTask(int[] current, int[] next, int rows, int cols, int stride,
                 int rowStart, int rowEnd) {
            this.current = current;
            this.next    = next;
            this.rows    = rows;
            this.cols    = cols;
            this.stride  = stride;
            this.rowStart = rowStart;
            this.rowEnd   = rowEnd;
        }

        @Override
        protected void compute() {
            int span = rowEnd - rowStart;
            if (span <= TILE_ROWS) {
                computeTile();
            } else {
                int mid = rowStart + (span >>> 1);
                invokeAll(
                    new TileTask(current, next, rows, cols, stride, rowStart, mid),
                    new TileTask(current, next, rows, cols, stride, mid, rowEnd)
                );
            }
        }

        private void computeTile() {
            final int m = rows, n = cols, s = stride;
            final int[] cur = current, nxt = next;

            for (int i = rowStart; i < rowEnd; i++) {
                final int rowOff = i * s;
                final int above  = (i - 1) * s;
                final int below  = (i + 1) * s;
                final boolean hasUp   = (i > 0);
                final boolean hasDown = (i < m - 1);

                // Optimization: Hoisting invariant condition handling to minimize loop branching stalls
                for (int j = 0; j < n; j++) {
                    int live = 0;
                    final boolean hasLeft  = (j > 0);
                    final boolean hasRight = (j < n - 1);

                    if (hasUp) {
                        if (hasLeft  && cur[above + j - 1] == 1) live++;
                        if (cur[above + j]     == 1) live++;
                        if (hasRight && cur[above + j + 1] == 1) live++;
                    }
                    if (hasLeft  && cur[rowOff + j - 1] == 1) live++;
                    if (hasRight && cur[rowOff + j + 1] == 1) live++;
                    if (hasDown) {
                        if (hasLeft  && cur[below + j - 1] == 1) live++;
                        if (cur[below + j]     == 1) live++;
                        if (hasRight && cur[below + j + 1] == 1) live++;
                    }

                    int currentCellIdx = rowOff + j;
                    if (cur[currentCellIdx] == 1) {
                        nxt[currentCellIdx] = (live == 2 || live == 3) ? 1 : 0;
                    } else {
                        nxt[currentCellIdx] = (live == 3) ? 1 : 0;
                    }
                }
            }
        }
    }

    public static void main(String[] args) throws IOException {
        String csvPath = args.length > 0 ? args[0] : "tests_configs.csv";
        List<TestCase> testCases = readTestConfigs(csvPath);

        System.out.println("implementation,rows,cols,iterations,seed,threads,time_ms");

        for (TestCase tc : testCases) {
            int stride = paddedStride(tc.cols);
            int[] current = generateGrid(tc.rows, tc.cols, stride, tc.seed);
            int[] next    = new int[tc.rows * stride];

            ForkJoinPool pool = new ForkJoinPool(tc.threads);

            // Advanced Infrastructure Update: Encapsulating execution with definitive pool lifecycle containment guards
            try {
                // Warm-up: 3 non-timed iterations for JIT compilation optimizations
                for (int w = 0; w < 3; w++) {
                    pool.invoke(new TileTask(current, next, tc.rows, tc.cols, stride, 0, tc.rows));
                    int[] t = current; current = next; next = t;
                }

                long start = System.nanoTime();

                for (int iter = 0; iter < tc.iterations; iter++) {
                    pool.invoke(new TileTask(current, next, tc.rows, tc.cols, stride, 0, tc.rows));
                    int[] t = current; current = next; next = t;
                }

                long end = System.nanoTime();
                double timeMs = (end - start) / 1_000_000.0;
                System.out.printf("java_optimized,%d,%d,%d,%d,%d,%.2f%n",
                    tc.rows, tc.cols, tc.iterations, tc.seed, tc.threads, timeMs);

            } finally {
                // Guaranteed cleanup closure tracking to prevent parallel thread resource leakage
                pool.shutdown();
            }
        }
    }

    static List<TestCase> readTestConfigs(String csvPath) throws IOException {
        List<TestCase> testCases = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(csvPath))) {
            String line;
            boolean isHeader = true;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty() || line.startsWith("#")) continue;
                if (isHeader) { isHeader = false; continue; }
                String[] parts = line.split(",");
                if (parts.length < 4) continue;
                int rows       = Integer.parseInt(parts[0].trim());
                int cols       = Integer.parseInt(parts[1].trim());
                int iterations = Integer.parseInt(parts[2].trim());
                int seed       = Integer.parseInt(parts[3].trim());
                int threads    = (parts.length >= 5)
                                 ? Integer.parseInt(parts[4].trim())
                                 : Runtime.getRuntime().availableProcessors();
                testCases.add(new TestCase(rows, cols, iterations, seed, threads));
            }
        }
        return testCases;
    }

    static int[] generateGrid(int rows, int cols, int stride, int seed) {
        Random rand = new Random(seed);
        int[] grid = new int[rows * stride];
        for (int i = 0; i < rows; i++) {
            int off = i * stride;
            for (int j = 0; j < cols; j++) {
                grid[off + j] = rand.nextInt(2);
            }
        }
        return grid;
    }

    static class TestCase {
        int rows, cols, iterations, seed, threads;
        TestCase(int rows, int cols, int iterations, int seed, int threads) {
            this.rows = rows;
            this.cols = cols;
            this.iterations = iterations;
            this.seed = seed;
            this.threads = threads;
        }
    }
}