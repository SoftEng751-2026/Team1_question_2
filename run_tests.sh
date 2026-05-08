set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RESULTS_DIR="benchmark_results/perf_raw"
mkdir -p "$RESULTS_DIR"
OUT="$RESULTS_DIR/all_results.csv"

echo "implementation,rows,cols,iterations,seed,threads,time_ms" > "$OUT"



echo -e "\n=== Compiling C++ Optimized (OpenMP) ==="
g++ -O3 -fopenmp Cpp_implementation/Cpp_fork_optimized.cpp -o Cpp_implementation/Cpp_fork_optimized.exe

echo -e "\n=== Compiling C++ Sequential ==="
g++ -O3 -fopenmp Cpp_implementation/Cpp_sequential.cpp -o Cpp_implementation/Cpp_sequential.exe

echo -e "\n=== Running: C++ Optimized (OpenMP + cache) ==="
./Cpp_implementation/Cpp_fork_optimized.exe tests_configs.csv | tee /dev/stderr | tail -n +2 >> "$OUT"

echo -e "\n=== Running: C++ Sequential ==="
./Cpp_implementation/Cpp_sequential.exe tests_configs.csv | tee /dev/stderr | tail -n +2 >> "$OUT"

echo -e "\n=== Compiling Java Files ==="
javac Java_implementation/*.java

echo -e "\n=== Running: Java Optimized (ForkJoin + cache) ==="
java -cp . Java_implementation.Game_of_life_fork_optimized "tests_configs.csv" | tee /dev/stderr | tail -n +2 >> "$OUT"

echo -e "\n=== Running: Java Sequential ==="
java -cp . Java_implementation.Sequential_test "tests_configs.csv" | tee /dev/stderr | tail -n +2 >> "$OUT"

rm -f Java_implementation/*.class
rm -f Cpp_implementation/*.exe

echo -e "\n=== Generating Performance Plots ==="
python create_plot.py



echo -e "\n=== All results saved to $OUT ==="
echo "Rows in CSV (excluding header): $(tail -n +2 "$OUT" | wc -l)"