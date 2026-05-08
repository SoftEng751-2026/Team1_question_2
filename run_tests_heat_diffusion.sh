set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RESULTS_DIR="benchmark_results/perf_raw"
mkdir -p "$RESULTS_DIR"
HEAT_OUT="$RESULTS_DIR/heat_diffusion_results.csv"

echo "implementation,rows,cols,iterations,seed,threads,time_ms" > "$HEAT_OUT"

echo -e "\n=== Compiling Java Heat Diffusion ==="
javac Java_implementation/Heat_diffusion_benchmark.java

echo -e "\n=== Compiling C++ Heat Diffusion (OpenMP) ==="
g++ -O3 -fopenmp Cpp_implementation/Heat_diffusion_benchmark.cpp -o Cpp_implementation/Heat_diffusion_benchmark.exe

echo -e "\n=== Running: Java Heat Diffusion Benchmark ==="
java -cp . Java_implementation.Heat_diffusion_benchmark "tests_configs.csv" | tee /dev/stderr | tail -n +2 >> "$HEAT_OUT"

echo -e "\n=== Running: C++ Heat Diffusion Benchmark ==="
./Cpp_implementation/Heat_diffusion_benchmark.exe tests_configs.csv | tee /dev/stderr | tail -n +2 >> "$HEAT_OUT"

echo -e "\n=== Generating Heat Diffusion Performance Plots ==="
python create_plot_heat_diffusion.py

rm -f Java_implementation/*.class
rm -f Cpp_implementation/*.exe

echo -e "\n=== Heat Diffusion results saved to $HEAT_OUT ==="
echo "Rows in CSV (excluding header): $(tail -n +2 "$HEAT_OUT" | wc -l)"