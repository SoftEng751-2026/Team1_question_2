package Java_implementation;
public class TestCase {
    int rows, cols, iterations, seed, threads;
    TestCase(int rows, int cols, int iterations, int seed) {
        this(rows, cols, iterations, seed, Runtime.getRuntime().availableProcessors());
    }
    TestCase(int rows, int cols, int iterations, int seed, int threads) {
        this.rows = rows;
        this.cols = cols;
        this.iterations = iterations;
        this.seed = seed;
        this.threads = threads;
    }
}