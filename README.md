Heat Diffusion Simulation (Parallel Implementation)
This project implements a parallelized 2D heat diffusion simulation using a 5-point stencil method in both C++ and Java.

Implementation,Framework,Execution Time
C++,OpenMP (#pragma omp parallel for),0.0263 seconds
Java,ForkJoin Framework (RecursiveAction),0.128 seconds
Technical Implementation Details
C++ (OpenMP)
Parallelization: Uses #include <omp.h> and the #pragma omp parallel for directive to split the grid rows across available CPU cores.

Scheduling: Employs static scheduling for the stencil computation to minimize thread management overhead.

Timing: Captured using omp_get_wtime() for high-precision parallel benchmarking.

Java (ForkJoin)
Framework: Utilizes ForkJoinPool and RecursiveAction to recursively divide the workload.

Optimization: Uses a THRESHOLD of 64 rows to maintain cache-line efficiency and balance task granularity.

Environment Fix: Requires the -encoding UTF-8 flag during compilation in Linux/Docker environments to handle special characters in comments.

How to Run in Docker
C++ Compilation & Execution
Bash
g++ -O3 -fopenmp heat_diffusion.cpp -o heat_diffusion_parallel
./heat_diffusion_parallel 1000 100
Java Compilation & Execution
Bash
javac -encoding UTF-8 HeatDiffusion.java
java HeatDiffusion
