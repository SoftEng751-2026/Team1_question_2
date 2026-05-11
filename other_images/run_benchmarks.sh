#!/bin/bash

# Set paths
CPP_FILE="./Layout_comparison_benchmark.cpp"
JAVA_FILE="./LayoutComparisonBenchmark.java"
ITERATIONS=1000
SIZES="512 1024 2048"

echo "Cleaning up..."
rm -f layout_cpp results.csv

echo "Compiling C++..."
g++ -O3 "$CPP_FILE" -o layout_cpp

echo "Compiling Java..."
# Compile with -d . to respect the package structure
javac -d . "$JAVA_FILE"

echo "Size,Type,Language,Time" > results.csv

for N in $SIZES
do
    echo "---------------------------------------"
    echo "Testing Grid Size: ${N}x${N}"
    
    # Run C++ Benchmark
    echo "Running C++..."
    cpp_out=$(./layout_cpp $N $ITERATIONS)
    t1d_cpp=$(echo "$cpp_out" | grep "FINAL_1D_TIME" | awk '{print $2}')
    t2d_cpp=$(echo "$cpp_out" | grep "FINAL_2D_TIME" | awk '{print $2}')
    
    echo "$N,1D,CPP,$t1d_cpp" >> results.csv
    echo "$N,2D,CPP,$t2d_cpp" >> results.csv
    
    # Run Java Benchmark
    echo "Running Java..."
    # Using the package name defined in the source
    java_out=$(java assignment.stencil.LayoutComparisonBenchmark $N $ITERATIONS)
    t1d_java=$(echo "$java_out" | grep "FINAL_1D_TIME" | awk '{print $2}')
    t2d_java=$(echo "$java_out" | grep "FINAL_2D_TIME" | awk '{print $2}')
    
    echo "$N,1D,Java,$t1d_java" >> results.csv
    echo "$N,2D,Java,$t2d_java" >> results.csv
done

echo "---------------------------------------"
echo "Benchmark Complete. Results saved to results.csv"
if command -v python3 &>/dev/null; then
    echo "Generating plot..."
    python3 plot_results.py
fi