# ai-dan-cpp

## Requirements
- CMake@3.28.3+
- g++@13.3.0+
- Python@3.12.3+
- libprotoc@3.21.12+

## Install
### Protobuf
**Ubuntu/Debian**
```
sudo apt-get install -y protobuf-compiler libprotobuf-dev
```

**Mac**
```
brew install protobuf
```

## Compile
From the root directory, run:
```sh
mkdir build \
cd build \
cmake -DCMAKE_BUILD_TYPE=Debug .. &&
cmake --build . --parlallel
```

### Compile in debug mode:

```sh
cmake -DCMAKE_BUILD_TYPE=Debug .. &&
make -j
```

Run:
```sh
./App -o test.bin
```

Run with performance metrics:
```sh
sudo perf stat -d -d -d ./App -o test.bin
```

### Compile in Release:

```sh
cmake -DCMAKE_BUILD_TYPE=Relase .. &&
make -j
```

## How to run
From the ./build directory, run `./App`

You can specify the following flags:
- "-o <output_directory>" - Output path of the model
- "-i <input_directory>" - Input path of the model
- "-b <batch_size>" - Batch size (for training)

# Debugging

```sh
# Enable core dumps
ulimit -c unlimited
```

Run the program, then use `gdb ./App core`, and run `bt` (backtrace) to see the 
stack trace where the program crashed
