Run Java tests:

```bash
# Java Implementations
javac Java_implementation/*.java

java -cp . Java_implementation.Sequential_test "tests_configs.csv"

java -cp . Java_implementation.Game_of_life_fork "tests_configs.csv"

# C++ Implementations
g++ Cpp_implementation/Cpp_sequential.cpp -o Cpp_implementation/Cpp_sequential.exe

./Cpp_implementation/Cpp_sequential.exe tests_configs.csv

g++ -O3 -fopenmp Cpp_implementation/Cpp_fork.cpp -o Cpp_implementation/Cpp_fork.exe

./Cpp_implementation/Cpp_fork.exe tests_configs.csv

```