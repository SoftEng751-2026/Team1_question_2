set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RESULTS_DIR="benchmark_results/perf_raw"
mkdir -p "$RESULTS_DIR"
OUT="$RESULTS_DIR/all_results.csv"

NUM_RUNS=5
echo "implementation,rows,cols,iterations,seed,threads,time_ms,run" > "$OUT"

echo -e "\n=== Compiling C++ Optimized (OpenMP) ==="
g++ -O3 -fopenmp Cpp_implementation/Cpp_fork_optimized.cpp -o Cpp_implementation/Cpp_fork_optimized.exe

echo -e "\n=== Compiling C++ Sequential ==="
g++ -O3 -fopenmp Cpp_implementation/Cpp_sequential.cpp -o Cpp_implementation/Cpp_sequential.exe

echo -e "\n=== Running: C++ Optimized (OpenMP + cache) ==="
for run in $(seq 1 $NUM_RUNS); do
    echo "  Run $run..." >&2
    ./Cpp_implementation/Cpp_fork_optimized.exe tests_configs.csv | tail -n +2 | sed "s/$/,$run/" >> "$OUT"
done

echo -e "\n=== Running: C++ Sequential ==="
for run in $(seq 1 $NUM_RUNS); do
    echo "  Run $run..." >&2
    ./Cpp_implementation/Cpp_sequential.exe tests_configs.csv | tail -n +2 | sed "s/$/,$run/" >> "$OUT"
done

echo -e "\n=== Compiling Java Files ==="
javac Java_implementation/*.java

echo -e "\n=== Running: Java Optimized (ForkJoin + cache) ==="
for run in $(seq 1 $NUM_RUNS); do
    echo "  Run $run..." >&2
    java -cp . Java_implementation.Game_of_life_fork_optimized "tests_configs.csv" | tail -n +2 | sed "s/$/,$run/" >> "$OUT"
done

echo -e "\n=== Running: Java Sequential ==="
for run in $(seq 1 $NUM_RUNS); do
    echo "  Run $run..." >&2
    java -cp . Java_implementation.Sequential_test "tests_configs.csv" | tail -n +2 | sed "s/$/,$run/" >> "$OUT"
done

rm -f Java_implementation/*.class
rm -f Cpp_implementation/*.exe

echo -e "\n=== Generating Performance Plots ==="
python create_analysis_plots.py

echo -e "\n=== All results saved to $OUT ==="
echo "Rows in CSV (excluding header): $(tail -n +2 "$OUT" | wc -l)"