cmake_minimum_required(VERSION 3.5)

set(CMAKE_CXX_STANDARD 14)

project(actor-model)

# If conan is being used, configure CMake to use conan for dependencies.
include(${CMAKE_BINARY_DIR}/conan_paths.cmake)


add_subdirectory(src)
