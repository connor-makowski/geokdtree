cmake_minimum_required(VERSION 3.14)
project(geokdtree)

# -----------------------------
# Set C++ standard
# -----------------------------
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# -----------------------------
# Find Packages
# -----------------------------
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# -----------------------------
# Add nanobind
# -----------------------------
include(FetchContent)
FetchContent_Declare(
    nanobind
    GIT_REPOSITORY https://github.com/wjakob/nanobind.git
    GIT_TAG v2.9.2  # Specify the version you want
    GIT_SHALLOW TRUE  # Only fetch the specific commit, faster download
)
FetchContent_MakeAvailable(nanobind)

# -----------------------------
# KDTree module
# -----------------------------
nanobind_add_module(geokdtree_cpp
    bindings/geokdtree_bindings.cpp
    src/geokdtree.cpp
)
target_compile_features(geokdtree_cpp PRIVATE cxx_std_17)