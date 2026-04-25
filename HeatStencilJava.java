import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveAction;
import java.util.stream.IntStream;

public class HeatStencilJava {

    // Grid size N x N
    private final int N;

    // Number of stencil iterations
    private final int iterations;

    // Current grid and next grid (double buffering)
    private double[] u;
    private double[] uNew;

    // ForkJoin thread pool
    private final ForkJoinPool pool;

    public HeatStencilJava(int N, int iterations, int parallelism) {
        this.N = N;
        this.iterations = iterations;
        this.u = new double[N * N];
        this.uNew = new double[N * N];
        this.pool = new ForkJoinPool(parallelism);
        initGrid();
    }

    // Initialize grid: boundary = 1.0, interior = 0.0
    private void initGrid() {
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                int idx = i * N + j;
                if (i == 0 || i == N - 1 || j == 0 || j == N - 1) {
                    u[idx] = 1.0;  // fixed boundary
                } else {
                    u[idx] = 0.0;
                }
            }
        }
    }

    // Sequential 5‑point stencil update
    private void stepSequential() {
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

        copyBoundary(u, uNew);
        swapArrays();
    }

    // Parallel stencil using ForkJoin
    private void stepParallelForkJoin() {
        StencilTask root = new StencilTask(u, uNew, N, 1, N - 1);
        pool.invoke(root);
        copyBoundary(u, uNew);
        swapArrays();
    }

    // Parallel stencil using Java parallel streams
    private void stepParallelStream() {
        IntStream.range(1, N - 1).parallel().forEach(i -> {
            for (int j = 1; j < N - 1; j++) {
                int idx = i * N + j;

                double up = u[idx - N];
                double down = u[idx + N];
                double left = u[idx - 1];
                double right = u[idx + 1];

                uNew[idx] = 0.25 * (up + down + left + right);
            }
        });

        copyBoundary(u, uNew);
        swapArrays();
    }

    // Copy boundary values (boundary is fixed)
    private static void copyBoundary(double[] src, double[] dst) {
        int N = (int) Math.sqrt(src.length);

        // Top and bottom rows
        for (int j = 0; j < N; j++) {
            dst[j] = src[j];
            dst[(N - 1) * N + j] = src[(N - 1) * N + j];
        }

        // Left and right columns
        for (int i = 0; i < N; i++) {
            dst[i * N] = src[i * N];
            dst[i * N + (N - 1)] = src[i * N + (N - 1)];
        }
    }

    // Swap references to u and uNew
    private void swapArrays() {
        double[] tmp = u;
        u = uNew;
        uNew = tmp;
    }

    // Run sequential version and measure time
    public long runSequential() {
        initGrid();
        long start = System.nanoTime();
        for (int it = 0; it < iterations; it++) {
            stepSequential();
        }
        return System.nanoTime() - start;
    }

    // Run ForkJoin version and measure time
    public long runParallelForkJoin() {
        initGrid();
        long start = System.nanoTime();
        for (int it = 0; it < iterations; it++) {
            stepParallelForkJoin();
        }
        return System.nanoTime() - start;
    }

    // Run parallel stream version and measure time
    public long runParallelStream() {
        initGrid();
        long start = System.nanoTime();
        for (int it = 0; it < iterations; it++) {
            stepParallelStream();
        }
        return System.nanoTime() - start;
    }

    // Compute checksum to prevent dead‑code elimination
    public double checksum() {
        double sum = 0.0;
        for (double v : u) sum += v;
        return sum;
    }

    // ForkJoin task for row‑range stencil update
    private static class StencilTask extends RecursiveAction {
        private static final int THRESHOLD = 64;

        private final double[] u;
        private final double[] uNew;
        private final int N;
        private final int rowStart;
        private final int rowEnd;

        StencilTask(double[] u, double[] uNew, int N, int rowStart, int rowEnd) {
            this.u = u;
            this.uNew = uNew;
            this.N = N;
            this.rowStart = rowStart;
            this.rowEnd = rowEnd;
        }

        @Override
        protected void compute() {
            if (rowEnd - rowStart <= THRESHOLD) {
                // Direct computation for small row range
                for (int i = rowStart; i < rowEnd; i++) {
                    for (int j = 1; j < N - 1; j++) {
                        int idx = i * N + j;

                        double up = u[idx - N];
                        double down = u[idx + N];
                        double left = u[idx - 1];
                        double right = u[idx + 1];

                        uNew[idx] = 0.25 * (up + down + left + right);
                    }
                }
            } else {
                // Split task into two halves
                int mid = (rowStart + rowEnd) / 2;
                invokeAll(
                    new StencilTask(u, uNew, N, rowStart, mid),
                    new StencilTask(u, uNew, N, mid, rowEnd)
                );
            }
        }
    }

    public static void main(String[] args) {
        int N = 2048;
        int iterations = 200;
        int parallelism = Runtime.getRuntime().availableProcessors();

        if (args.length >= 1) N = Integer.parseInt(args[0]);
        if (args.length >= 2) iterations = Integer.parseInt(args[1]);
        if (args.length >= 3) parallelism = Integer.parseInt(args[2]);

        HeatStencilJava solver = new HeatStencilJava(N, iterations, parallelism);

        // Warm‑up
        solver.runSequential();
        solver.runParallelForkJoin();
        solver.runParallelStream();

        long tSeq = solver.runSequential();
        long tFj = solver.runParallelForkJoin();
        long tPs = solver.runParallelStream();

        System.out.printf("Sequential: %.3f ms, checksum = %.6f%n",
                tSeq / 1e6, solver.checksum());

        System.out.printf("ForkJoin: %.3f ms, checksum = %.6f, speedup = %.2f%n",
                tFj / 1e6, solver.checksum(), (double) tSeq / tFj);

        System.out.printf("ParallelStream: %.3f ms, checksum = %.6f, speedup = %.2f%n",
                tPs / 1e6, solver.checksum(), (double) tSeq / tPs);
    }
}
