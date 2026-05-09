## Game of Life Stencil Analysis

Project compares two parallelised versions of the game of life problem in C++ and Java. Multiple tests of varying grid sizes,iterations, seeds, and threads are ran according to how many cores and logical processors I have. To change these according to yours manually go to test_configs.csv to change thread count and tests. After testing script is ran, a bar chart is created to see the peformance differences in benchmark_results/benchmark_plots.
***
For everything to work you must have JDK/Java 11 and GCC/G++ and python 3.10.
Easier to use WSL or a Linux environment to run the tests. 
Or use the dockerfile given and then run the image with volume.
***


**Run the Java fork vs C++ fork script**
```bash
# If using WSL make sure you have dos2unix

sudo apt update && sudo apt install -y dos2unix
dos2unix run_tests.sh
dos2unix run_tests_heat_diffusion.sh


./run_tests.sh
./run_tests_heat_diffusion.sh

# If no python installed in your linux env go out and run
python create_plot.py
python create_plot_heat_diffusion.py
python create_analysis_plots.py
```

***
**Run with docker (for assessors and team):**
```bash
docker build -t stencil_benchmark .

# If you're on windows
docker run --rm -v "%cd%":/app stencil_benchmark

# If you're on WSL or Mac
docker run --rm -v $(pwd):/app stencil_benchmark
```

