find_package(GTest CONFIG REQUIRED)

add_executable(test_widget test_widget.cpp)
target_link_libraries(test_widget
  PRIVATE
    widget
    GTest::gtest
    GTest::gtest_main
)

include(GoogleTest)
gtest_discover_tests(test_widget)
