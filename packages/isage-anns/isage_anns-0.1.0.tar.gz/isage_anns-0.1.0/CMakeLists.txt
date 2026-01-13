cmake_minimum_required(VERSION 3.10...3.27)
project(
    sage-anns
    VERSION 0.1.0
    LANGUAGES CXX C
)

# ============================================================================
# Global Build Settings
# ============================================================================
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_C_STANDARD 11)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Compilation flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -fPIC")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0")

# ============================================================================
# Find Dependencies
# ============================================================================
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

message(STATUS "")
message(STATUS "=== SAGE ANNS Build Configuration ===")
message(STATUS "Python: ${Python_VERSION}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "======================================")
message(STATUS "")

# ============================================================================
# Add subdirectories for algorithm implementations
# ============================================================================

# Note: Each algorithm has its own CMakeLists.txt
# Uncomment to enable specific algorithms

# add_subdirectory(implementations/faiss)
# add_subdirectory(implementations/diskann-ms)
# add_subdirectory(implementations/candy)
# add_subdirectory(implementations/puck)
# add_subdirectory(implementations/SPTAG)

# ============================================================================
# Python Bindings
# ============================================================================
# Main Python bindings will be added here
# For now, each algorithm builds its own .so file

# ============================================================================
# Installation
# ============================================================================
if(NOT SKBUILD_STATE STREQUAL "editable")
    # Install Python source files
    install(
        DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/python/sage_anns/"
        DESTINATION "${SKBUILD_PLATLIB_DIR}/sage_anns"
        COMPONENT python
        FILES_MATCHING
        PATTERN "*.py"
        PATTERN "*.pyi"
        PATTERN "py.typed"
        PATTERN "__pycache__" EXCLUDE
        PATTERN "*.pyc" EXCLUDE
        PATTERN "tests" EXCLUDE
    )
endif()

# ============================================================================
# Build Summary
# ============================================================================
message(STATUS "")
message(STATUS "SAGE ANNS Build Summary")
message(STATUS "=========================================")
message(STATUS "Project: ${PROJECT_NAME} v${PROJECT_VERSION}")
message(STATUS "Python: ${Python_VERSION}")
message(STATUS "C++ Standard: C++${CMAKE_CXX_STANDARD}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "=========================================")
message(STATUS "")
