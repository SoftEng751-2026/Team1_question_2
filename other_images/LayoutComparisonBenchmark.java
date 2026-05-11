package assignment.stencil;

import java.util.Arrays;

/**
 * Performance benchmark comparing 1D flattened arrays vs 2D nested arrays in Java.
 * This helps demonstrate why memory locality is crucial for Stencil computations.
 */
public class LayoutComparisonBenchmark {

    private static final double ALPHA = 0.1;

    /**
     * Benchmark using a 1D flattened array: double[N * N]
     * Memory is contiguous, providing high cache locality.
     */
    public static void run1DBenchmark(int n, int iterations, boolean isWarmup) {
        double[] current = new double[n * n];
        double[] next = new double[n * n];

        // Initialize a heat source in the middle
        current[(n / 2) * n + (n / 2)] = 1000.0;

        long start = System.nanoTime();

        for (int t = 0; t < iterations; t++) {
            for (int i = 1; i < n - 1; i++) {
                int rowIdx = i * n;
                int prevIdx = (i - 1) * n;
                int nextIdx = (i + 1) * n;
                
                for (int j = 1; j < n - 1; j++) {
                    next[rowIdx + j] = current[rowIdx + j] + ALPHA * (
                        current[nextIdx + j] + current[prevIdx + j] +
                        current[rowIdx + j + 1] + current[rowIdx + j - 1] - 4.0 * current[rowIdx + j]
                    );
                }
            }
            // Swap buffers
            double[] temp = current;
            current = next;
            next = temp;
        }

        long end = System.nanoTime();
        double ms = (end - start) / 1_000_000.0;
        if (!isWarmup) {
            System.out.printf("FINAL_1D_TIME: %.2f\n", ms);
        }
    }

    /**
     * Benchmark using a 2D nested array: double[N][N]
     * Each row is a separate object in the heap, leading to potential cache misses.
     */
    public static void run2DBenchmark(int n, int iterations, boolean isWarmup) {
        double[][] current = new double[n][n];
        double[][] next = new double[n][n];

        // Initialize a heat source in the middle
        current[n / 2][n / 2] = 1000.0;

        long start = System.nanoTime();

        for (int t = 0; t < iterations; t++) {
            for (int i = 1; i < n - 1; i++) {
                // current[i] involves an additional pointer dereference
                double[] cRow = current[i];
                double[] pRow = current[i - 1];
                double[] nRow = current[i + 1];
                double[] nextRow = next[i];
                
                for (int j = 1; j < n - 1; j++) {
                    nextRow[j] = cRow[j] + ALPHA * (
                        nRow[j] + pRow[j] +
                        cRow[j + 1] + cRow[j - 1] - 4.0 * cRow[j]
                    );
                }
            }
            // Swap buffers
            double[][] temp = current;
            current = next;
            next = temp;
        }

        long end = System.nanoTime();
        double ms = (end - start) / 1_000_000.0;
        if (!isWarmup) {
            System.out.printf("FINAL_2D_TIME: %.2f\n", ms);
        }
    }

    public static void main(String[] args) {
        int n = 1024;
        int iterations = 2500;

        if (args.length >= 1) n = Integer.parseInt(args[0]);
        if (args.length >= 2) iterations = Integer.parseInt(args[1]);

        System.out.println("Starting Benchmark: Iterations = " + iterations);
        
        // Warm up the JVM (JIT compiler optimization)
        System.out.println("Warming up...");
        run1DBenchmark(512, 100, true);
        run2DBenchmark(512, 100, true);
        
        System.out.println("Running actual tests...");
        run1DBenchmark(n, iterations, false);
        run2DBenchmark(n, iterations, false);
    }
}