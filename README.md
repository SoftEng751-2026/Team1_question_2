For everything to work you must have JDK/Java 11 and GCC/G++.
Easier to use WSL or a Linux environment to run the tests.

Run ALL tests(just for sanity check):

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

Run the Java fork vs C++ fork script(actual assessment scope):
```bash
# If using WSL make sure you have dos2unix
sudo apt update && sudo apt install -y dos2unix
dos2unix run_tests.sh

./run_tests.sh
```