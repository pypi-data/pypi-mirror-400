cmake_minimum_required(VERSION 3.25)
project(App VERSION 1.0 LANGUAGES CXX C)
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include(FetchContent)

# ----------------------
# PyBind11
# ----------------------
FetchContent_Declare(
    PyBind
    URL https://github.com/pybind/pybind11/archive/refs/tags/v2.13.6.tar.gz
    DOWNLOAD_EXTRACT_TIMESTAMP true
)

FetchContent_MakeAvailable(PyBind)

# ----------------------
# Threading support
# ----------------------
find_package(Threads REQUIRED)

# ----------------------
# Recursively grab all .cpp files from src/
# ----------------------
file(GLOB_RECURSE SOURCES src/*.cpp)

# ----------------------
# Compiler flags by build type
# ----------------------
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -fsanitize=address -fno-omit-frame-pointer")

# Option for native CPU optimizations (disable for portable builds)
option(USE_NATIVE_ARCH "Use -march=native for CPU-specific optimizations" OFF)
if(USE_NATIVE_ARCH)
    set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG -march=native -fomit-frame-pointer -flto -fno-rtti")
else()
    set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG -fomit-frame-pointer -flto -fno-rtti")
endif()

# ----------------------
# Add executable
# ----------------------
add_executable(App ${SOURCES})

# ----------------------
# Include directories
# ----------------------
target_include_directories(App 
    PRIVATE 
        include
)

# ----------------------
# Link libraries
# ----------------------
target_link_libraries(App
    PRIVATE
        Threads::Threads
)

# ----------------------
# PyBind11 module target
# ----------------------
file(GLOB_RECURSE SOURCES_NO_MAIN src/*.cpp)
list(FILTER SOURCES_NO_MAIN EXCLUDE REGEX ".*main\\.cpp$")

pybind11_add_module(ai_dan python/bindings.cpp ${SOURCES_NO_MAIN})
target_include_directories(ai_dan PRIVATE include)
target_link_libraries(ai_dan PRIVATE Threads::Threads)
# Enable RTTI for pybind11 (required) and set visibility
target_compile_options(ai_dan PRIVATE -frtti -fvisibility=hidden)

# Install the Python module to root (single extension module)
install(TARGETS ai_dan LIBRARY DESTINATION . COMPONENT python)

# Enable LTO globally
include(CheckIPOSupported)
check_ipo_supported(RESULT lto_supported OUTPUT lto_output)
if(lto_supported)
    message(STATUS "IPO / LTO enabled")
    set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
else()
    message(WARNING "IPO / LTO not supported: ${lto_output}")
endif()

message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
