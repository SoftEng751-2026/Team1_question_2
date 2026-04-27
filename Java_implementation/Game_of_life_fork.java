package Java_implementation;
import java.io.*;
import java.util.*;
import java.util.concurrent.*;

class Game_of_life_fork {


    private static final int THRESHOLD = 64; 

    static class GameTask extends RecursiveAction {
        private final int[][] current;
        private final int[][] next;
        private final int startRow, endRow, m, n;

        GameTask(int[][] current, int[][] next, int startRow, int endRow, int m, int n) {
            this.current = current;
            this.next = next;
            this.startRow = startRow;
            this.endRow = endRow;
            this.m = m;
            this.n = n;
        }

        @Override
        protected void compute() {
            int rows = endRow - startRow;
            if (rows <= THRESHOLD) {
                computeDirectly();
            } else {
                int mid = startRow + (rows / 2);
                invokeAll(
                    new GameTask(current, next, startRow, mid, m, n),
                    new GameTask(current, next, mid, endRow, m, n)
                );
            }
        }

        private void computeDirectly() {
            int[][] directions = { { 0, 1 }, { 1, 0 }, { 0, -1 }, { -1, 0 },
                                   { 1, 1 }, { -1, -1 }, { 1, -1 }, { -1, 1 } };

            for (int i = startRow; i < endRow; i++) {
                for (int j = 0; j < n; j++) {
                    int live = 0;
                    for (int[] dir : directions) {
                        int x = i + dir[0], y = j + dir[1];
                        if (x >= 0 && x < m && y >= 0 && y < n && current[x][y] == 1) {
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
    }

    public static void main(String[] args) throws IOException {
        String csvPath = args.length > 0 ? args[0] : "tests_configs.csv";
        List<TestCase> testCases = readTestConfigs(csvPath);
        ForkJoinPool pool = ForkJoinPool.commonPool();

        System.out.println("implementation,rows,cols,iterations,seed,time_ms");

        for (TestCase tc : testCases) {
            int[][] current = generateGrid(tc.rows, tc.cols, tc.seed);
            int[][] next = new int[tc.rows][tc.cols];

            long start = System.nanoTime();

            for (int i = 0; i < tc.iterations; i++) {
                pool.invoke(new GameTask(current, next, 0, tc.rows, tc.rows, tc.cols));
                
                // Swap references for next iteration
                int[][] temp = current;
                current = next;
                next = temp;
            }
            long end = System.nanoTime();

            double timeMs = (end - start) / 1_000_000.0;
            System.out.printf("java_parallel,%d,%d,%d,%d,%.2f%n",
                tc.rows, tc.cols, tc.iterations, tc.seed, timeMs);
        }
    }

    
    static List<TestCase> readTestConfigs(String csvPath) throws IOException {
        List<TestCase> testCases = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(csvPath))) {
            String line;
            boolean isHeader = true;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty() || line.startsWith("#")) continue; // skip empty/comments
                if (isHeader) { isHeader = false; continue; } // skip header line "rows, cols, iterations, seed"
                String[] parts = line.split(",");
                if (parts.length != 4) continue; // skip malformed lines
                int rows = Integer.parseInt(parts[0].trim());
                int cols = Integer.parseInt(parts[1].trim());
                int iterations = Integer.parseInt(parts[2].trim());
                int seed = Integer.parseInt(parts[3].trim());
                testCases.add(new TestCase(rows, cols, iterations, seed));
            }
        }
        return testCases;
    }
    static int[][] generateGrid(int rows, int cols, int seed) {
        Random rand = new Random(seed);
        int[][] grid = new int[rows][cols];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                grid[i][j] = rand.nextInt(2); // 0 (dead) or 1 (alive), reproducible with same seed
            }
        }
        return grid;
    }
}