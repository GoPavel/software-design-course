find_package(caf)
find_package(catch2)

add_executable(actor-model main.cpp server.cpp)

target_link_libraries(actor-model caf::caf)

add_executable(actor-model-test test.cpp server.cpp)
target_link_libraries(actor-model-test caf::caf catch2::catch2)
