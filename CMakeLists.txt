cmake_minimum_required(VERSION 3.15)

# -----------------------------
# Define The Project
# -----------------------------
project(geokdtree LANGUAGES NONE)

# -----------------------------
# Build Options
# -----------------------------
option(SKIP_CPP_BUILD "Skip C++ extension module building" OFF)

# -----------------------------
# C++ detection
# -----------------------------
include(CheckLanguage)
check_language(CXX)

if(CMAKE_CXX_COMPILER)
    enable_language(CXX)
endif()


if(SKIP_CPP_BUILD)

        message(STATUS 
            "C++ build skipped. Using pure python version of geokdtree. Performance will be reduced."
        )

elseif(NOT CMAKE_CXX_COMPILER_LOADED)

    message(WARNING
        "No usable C++ compiler detected. Using pure python version of geokdtree. Performance will be reduced."
    )

else()

    message(STATUS 
        "C++ compiler detected: Building compiled extension."
    )

    # -----------------------------
    # Set C++ standard
    # -----------------------------
    set(CMAKE_CXX_STANDARD 20)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)

    # -----------------------------
    # OPTIMIZATION FLAGS
    # -----------------------------
    set(CMAKE_BUILD_TYPE Release)
    set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -DNDEBUG")

    # -----------------------------
    # Find Packages
    # -----------------------------
    find_package(Python 3.10 COMPONENTS Interpreter Development REQUIRED)

    # -----------------------------
    # Add nanobind
    # -----------------------------
    find_package(nanobind CONFIG REQUIRED)

    # -----------------------------
    # GeoKDTree module
    # -----------------------------
    nanobind_add_module(cpp
        STABLE_ABI
        geokdtree/cpp/bindings/geokdtree_bindings.cpp
        geokdtree/cpp/src/geokdtree.cpp
    )
    install(TARGETS cpp DESTINATION geokdtree)

endif()