set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RESULTS_DIR="benchmark_results/perf_raw"
mkdir -p "$RESULTS_DIR"
HEAT_OUT="$RESULTS_DIR/heat_diffusion_results.csv"
NUM_RUNS=5

echo "implementation,rows,cols,iterations,seed,threads,time_ms,run" > "$HEAT_OUT"

echo -e "\n=== Compiling Java Heat Diffusion ==="
javac Java_implementation/Heat_diffusion_benchmark.java

echo -e "\n=== Compiling C++ Heat Diffusion (OpenMP) ==="
g++ -O3 -fopenmp Cpp_implementation/Heat_diffusion_benchmark.cpp -o Cpp_implementation/Heat_diffusion_benchmark.exe

echo -e "\n=== Running: Java Heat Diffusion Serial ==="
for run in $(seq 1 $NUM_RUNS); do
    echo "  Run $run..." >&2
    java -cp . Java_implementation.Heat_diffusion_benchmark serial "tests_configs.csv" | tail -n +2 | sed "s/$/,$run/" >> "$HEAT_OUT"
done

echo -e "\n=== Running: Java Heat Diffusion Parallel (ForkJoin) ==="
for run in $(seq 1 $NUM_RUNS); do
    echo "  Run $run..." >&2
    java -cp . Java_implementation.Heat_diffusion_benchmark parallel "tests_configs.csv" | tail -n +2 | sed "s/$/,$run/" >> "$HEAT_OUT"
done

echo -e "\n=== Running: C++ Heat Diffusion Serial ==="
for run in $(seq 1 $NUM_RUNS); do
    echo "  Run $run..." >&2
    ./Cpp_implementation/Heat_diffusion_benchmark.exe serial tests_configs.csv | tail -n +2 | sed "s/$/,$run/" >> "$HEAT_OUT"
done

echo -e "\n=== Running: C++ Heat Diffusion Parallel (OpenMP) ==="
for run in $(seq 1 $NUM_RUNS); do
    echo "  Run $run..." >&2
    ./Cpp_implementation/Heat_diffusion_benchmark.exe parallel tests_configs.csv | tail -n +2 | sed "s/$/,$run/" >> "$HEAT_OUT"
done


rm -f Java_implementation/*.class
rm -f Cpp_implementation/*.exe

echo -e "\n=== Generating Heat Diffusion Performance Plots ==="
python3 create_plot_heat_diffusion.py
python3 create_analysis_plots.py



echo -e "\n=== Heat Diffusion results saved to $HEAT_OUT ==="
echo "Rows in CSV (excluding header): $(tail -n +2 "$HEAT_OUT" | wc -l)"