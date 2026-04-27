
package Java_implementation;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;



class Sequential_test {

    // Function to find the next generation
    static void findNextGen(int[][] mat) {
        int m = mat.length, n = mat[0].length;

        // Directions of eight possible neighbors
        int[][] directions = { { 0, 1 },  { 1, 0 },
                               { 0, -1 }, { -1, 0 },
                               { 1, 1 },  { -1, -1 },
                               { 1, -1 }, { -1, 1 } };

        // Iterate over the matrix
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                int live = 0;

                // Count the number of live neighbors
                for (int[] dir : directions) {
                    int x = i + dir[0], y = j + dir[1];

                    if (x >= 0 && x < m && y >= 0 && y < n
                        && (mat[x][y] == 1
                            || mat[x][y] == 3)) {
                        live++;
                    }
                }

                // If current cell is live and number of
                // live neighbors is less than 2 or greater
                // than 3, then the cell will die
                if (mat[i][j] == 1
                    && (live < 2 || live > 3)) {
                    mat[i][j] = 3;
                }

                // If current cell is dead and number of
                // live neighbors is equal to 3, then the
                // cell will become live
                else if (mat[i][j] == 0 && live == 3) {
                    mat[i][j] = 2;
                }
            }
        }

        // Update the matrix with the next generation
        // and print the results.
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {

                // value 2 represents the cell is live
                if (mat[i][j] == 2) {
                    mat[i][j] = 1;
                }

                // value 3 represents the cell is dead
                if (mat[i][j] == 3) {
                    mat[i][j] = 0;
                }

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


    public static void main(String[] args) throws IOException {
    
        String csvPath = args.length > 0 ? args[0] : "tests_configs.csv";
        List<TestCase> testCases = readTestConfigs(csvPath);
        
        System.out.println("implementation,rows,cols,iterations,seed,time_ms");
        
        for (TestCase tc : testCases) {
           
            int[][] grid = generateGrid(tc.rows, tc.cols, tc.seed);
            findNextGen(grid);
            long start = System.nanoTime();
            for (int i = 0; i < tc.iterations; i++) {
                findNextGen(grid);
            }
            long end = System.nanoTime();
            
            double timeMs = (end - start) / 1_000_000.0;
            System.out.printf("java_sequential,%d,%d,%d,%d,%.2f%n",
                tc.rows, tc.cols, tc.iterations, tc.seed, timeMs);
        }
    }
}

