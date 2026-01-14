cmake_minimum_required(VERSION 3.15...3.27)
project(pyovf VERSION 1.0.0 LANGUAGES CXX)

# C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Find Python and pybind11
# Note: PYTHON_EXECUTABLE is passed from setup.py via -DPYTHON_EXECUTABLE=...
# Must set before find_package to ensure correct Python version is used
if(PYTHON_EXECUTABLE)
    set(Python3_EXECUTABLE ${PYTHON_EXECUTABLE})
endif()
find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG QUIET)

if(NOT pybind11_FOUND)
    # Fetch pybind11 if not found
    include(FetchContent)
    FetchContent_Declare(
        pybind11
        GIT_REPOSITORY https://github.com/pybind/pybind11.git
        GIT_TAG v2.11.1
    )
    FetchContent_MakeAvailable(pybind11)
endif()

# Find ovf-rw sources
set(OVF_RW_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../ovf-rw")
if(NOT EXISTS "${OVF_RW_DIR}")
    set(OVF_RW_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src/pyovf/ovf-rw")
endif()

if(NOT EXISTS "${OVF_RW_DIR}/src_c++/OVF_File.cpp")
    message(FATAL_ERROR "Could not find OVF_File.cpp in ${OVF_RW_DIR}")
endif()

# Create the Python module
pybind11_add_module(_ovf_core MODULE
    src/pyovf/bindings/ovf_bindings.cpp
    ${OVF_RW_DIR}/src_c++/OVF_File.cpp
)

target_include_directories(_ovf_core PRIVATE
    ${OVF_RW_DIR}/src_c++
)

target_compile_definitions(_ovf_core PRIVATE
    BINDING  # Tells OVF_File not to delete data (Python/NumPy manages memory)
)

# Compiler-specific options
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(_ovf_core PRIVATE -Wall -Wextra -O3)
elseif(MSVC)
    target_compile_options(_ovf_core PRIVATE /W4 /O2)
endif()

# Install target
install(TARGETS _ovf_core DESTINATION pyovf)