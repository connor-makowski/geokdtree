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
if(NOT SKIP_CPP_BUILD)
    include(CheckLanguage)
    check_language(CXX)

    if(CMAKE_CXX_COMPILER)
        enable_language(CXX OPTIONAL)
    endif()
endif()


if(SKIP_CPP_BUILD)

    message(STATUS 
        "C++ build skipped. Using pure python version. Performance will be reduced."
    )

elseif(NOT CMAKE_CXX_COMPILER_LOADED)

    message(WARNING
        "No usable C++ compiler detected. Using pure python version. Performance will be reduced."
    )

else()

    # -----------------------------
    # Find Packages
    # -----------------------------
    find_package(Python 3.10 COMPONENTS Interpreter Development.Module QUIET)
    find_package(nanobind CONFIG QUIET)

    if(Python_FOUND AND nanobind_FOUND)
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
        if(MSVC)
            set(CMAKE_CXX_FLAGS_RELEASE "/O2 /DNDEBUG")
        else()
            set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -DNDEBUG")
        endif()

        # -----------------------------
        # GeoKDTree module
        # -----------------------------
        nanobind_add_module(cpp
            STABLE_ABI
            geokdtree/cpp/bindings/geokdtree_bindings.cpp
            geokdtree/cpp/src/geokdtree.cpp
        )
        install(TARGETS cpp DESTINATION geokdtree)
    else()
        message(WARNING
            "Python development headers or nanobind not found. Using pure python version. Performance will be reduced."
        )
    endif()

endif()

# -----------------------------
# Install Python package files
# -----------------------------
install(DIRECTORY geokdtree DESTINATION . FILES_MATCHING PATTERN "*.py")