add_library(widget
  lib/widget.cpp
  lib/widget.hpp
)
target_include_directories(widget PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/lib)

find_package(fmt CONFIG REQUIRED)
find_package(spdlog CONFIG REQUIRED)
target_link_libraries(widget PUBLIC fmt::fmt spdlog::spdlog)

add_executable(myproject main.cpp)
target_link_libraries(myproject PRIVATE widget)
