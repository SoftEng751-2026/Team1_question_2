set -e  
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo -e "\n=== Compiling Java Files ==="
javac Java_implementation/*.java
echo -e "\n=== Java Fork Test Results ==="
java -cp . Java_implementation.Game_of_life_fork "tests_configs.csv"
echo -e "\n=== Compiling C++ Fork (O3 + OpenMP) ==="
g++ -O3 -fopenmp Cpp_implementation/Cpp_fork.cpp -o Cpp_implementation/Cpp_fork.exe
echo -e "\n=== C++ Fork Test Results ==="
./Cpp_implementation/Cpp_fork.exe tests_configs.csv