package Java_implementation;

import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveAction;
import java.io.*;
import java.util.*;

public class Heat_diffusion_benchmark {
    
    /**
     * Internal class for parallelizing the diffusion stencil.
     */
    static class DiffusionTask extends RecursiveAction {
        private final int startRow, endRow, rows, cols;
        private final double[] src, dst;
        private final double alpha;
        private static final int THRESHOLD = 5000; // Granularity: prevents task-creation overhead
        private static final int TILE_SIZE = 32;   // Cache optimization: Tiling block size

        DiffusionTask(int startRow, int endRow, int rows, int cols, double[] src, double[] dst, double alpha) {
            this.startRow = startRow;
            this.endRow = endRow;
            this.rows = rows;
            this.cols = cols;
            this.src = src;
            this.dst = dst;
            this.alpha = alpha;
        }

        @Override
        protected void compute() {
            // Shared Memory Parallelism & Cache Optimization:
            // We stop recursion when the task size reaches a THRESHOLD or a specific row count.
            // This prevents the overhead of task creation from exceeding the actual computation time.
            // Splitting primarily by rows ensures that each task works on a contiguous memory block.
            if ((endRow - startRow) < (rows / 32) || (endRow - startRow) * cols < THRESHOLD) {
                int effectiveStart = Math.max(1, startRow);
                int effectiveEnd = Math.min(rows - 1, endRow);

                // Apply Tiling (Loop Blocking) even in the parallel leaf task 
                // to maximize Cache reuse.
                for (int ii = effectiveStart; ii < effectiveEnd; ii += TILE_SIZE) {
                    int limitI = Math.min(ii + TILE_SIZE, effectiveEnd);
                    for (int jj = 1; jj < cols - 1; jj += TILE_SIZE) {
                        int limitJ = Math.min(jj + TILE_SIZE, cols - 1);

                        for (int i = ii; i < limitI; i++) {
                            int rowOffset = i * cols;
                            int nextRow = (i + 1) * cols;
                            int prevRow = (i - 1) * cols;
                            for (int j = jj; j < limitJ; j++) {
                                int idx = rowOffset + j;
                                dst[idx] = src[idx] + alpha * (
                                    src[nextRow + j] +
                                    src[prevRow + j] +
                                    src[idx + 1] +
                                    src[idx - 1] -
                                    4.0 * src[idx]
                                );
                            }
                        }
                    }
                }
            } else {
                int mid = (startRow + endRow) / 2;
                invokeAll(new DiffusionTask(startRow, mid, rows, cols, src, dst, alpha),
                          new DiffusionTask(mid, endRow, rows, cols, src, dst, alpha));
            }
        }
    }

    public static void solveParallel(int rows, int cols, int iterations, int seed, int threads) {
        // Memory Optimization: 1D array flattening.
        // Java 2D arrays (double[][]) are arrays of objects, which causes "pointer chasing"
        // and cache misses. A flat 1D array ensures spatial locality.
        double[] current = new double[rows * cols];
        double[] next = new double[rows * cols];
        
        // Stability Parameter: In explicit 2D schemes, alpha must be <= 0.25 to stay stable.
        double alpha = 0.1; 

        current[(rows / 2) * cols + (cols / 2)] = (double)seed * 10.0;

        // Shared Memory Parallelism: Utilizing ForkJoinPool for work-stealing multitasking.
        ForkJoinPool pool = new ForkJoinPool(threads);
        long startTime = System.nanoTime();

        for (int t = 0; t < iterations; t++) {
            pool.invoke(new DiffusionTask(1, rows - 1, rows, cols, current, next, alpha));
            // Swap buffer references
            double[] temp = current;
            current = next;
            next = temp;
        }

        long endTime = System.nanoTime();
        long durationMs = (endTime - startTime) / 1_000_000;
        pool.shutdown();

        System.out.printf("HeatDiffusion_Java_ForkJoin,%d,%d,%d,%d,%d,%d\n", 
                          rows, cols, iterations, seed, threads, durationMs);
    }

    public static void solveSequential(int rows, int cols, int iterations, int seed, int threads) {
        double[] current = new double[rows * cols];
        double[] next = new double[rows * cols];
        double alpha = 0.1;

        current[(rows / 2) * cols + (cols / 2)] = (double)seed * 10.0;

        long startTime = System.nanoTime();

        for (int t = 0; t < iterations; t++) {
            // Sequential version also uses 2D Tiling (Loop Blocking)
            // This ensures the comparison against Parallel versions is about
            // multi-threading speedup, not just different cache-access patterns.
            final int TILE_SIZE = 32;
            for (int ii = 1; ii < rows - 1; ii += TILE_SIZE) {
                int endI = Math.min(ii + TILE_SIZE, rows - 1);
                for (int jj = 1; jj < cols - 1; jj += TILE_SIZE) {
                    int endJ = Math.min(jj + TILE_SIZE, cols - 1);
                    
                    for (int i = ii; i < endI; i++) {
                        int rowOffset = i * cols;
                        int nextRow = (i + 1) * cols;
                        int prevRow = (i - 1) * cols;
                        
                        for (int j = jj; j < endJ; j++) {
                            int idx = rowOffset + j;
                            next[idx] = current[idx] + alpha * (
                                current[nextRow + j] + 
                                current[prevRow + j] +
                                current[idx + 1] + 
                                current[idx - 1] - 
                                4.0 * current[idx]);
                        }
                    }
                }
            }
            // Double Buffering: Avoids copying data by swapping references between 'current' and 'next'.
            double[] temp = current; 
            current = next;
            next = temp;
        }

        long endTime = System.nanoTime();
        long durationMs = (endTime - startTime) / 1_000_000;
        System.out.printf("HeatDiffusion_Java_Serial,%d,%d,%d,%d,%d,%d\n", 
                          rows, cols, iterations, seed, threads, durationMs);
    }

    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Usage: java Heat_diffusion_benchmark <mode> <config_csv>");
            System.err.println("  mode: sequential | parallel");
            return;
        }

        String mode = args[0];
        System.out.println("implementation,rows,cols,iterations,seed,threads,time_ms");

        try (BufferedReader br = new BufferedReader(new FileReader(args[1]))) {
            String line = br.readLine(); // Skip header
            while ((line = br.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length >= 5) {
                    int rows = Integer.parseInt(parts[0].trim());
                    int cols = Integer.parseInt(parts[1].trim());
                    int iters = Integer.parseInt(parts[2].trim());
                    int seed = Integer.parseInt(parts[3].trim());
                    int threads = Integer.parseInt(parts[4].trim());
                    if ("parallel".equals(mode)) {
                        solveParallel(rows, cols, iters, seed, threads);
                    } else {
                        solveSequential(rows, cols, iters, seed, threads);
                    }
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}