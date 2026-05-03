# Architecture

`myproject` is a small C++20 starter project built with CMake, vcpkg,
GoogleTest, and CTest. The project separates the reusable `widget` library from
the executable and unit tests.

![Architecture](img/architecture.svg)

## Source Layout

```text
myproject/
+-- CMakeLists.txt
+-- CMakePresets.json
+-- vcpkg.json
+-- src/
|   +-- CMakeLists.txt
|   +-- main.cpp
|   +-- lib/
|       +-- widget.hpp
|       +-- widget.cpp
+-- tests/
    +-- CMakeLists.txt
    +-- test_widget.cpp
```

## Build Targets

- `widget` is the library target. It owns the public header in `src/lib/` and
  the implementation in `src/lib/widget.cpp`.
- `myproject` is the executable target. It links `widget` and prints a sample
  description.
- `test_widget` is the GoogleTest executable. CTest discovers the individual
  test cases through `gtest_discover_tests`.

## Dependency Direction

Dependencies flow inward toward the `widget` library:

- `src/main.cpp` depends on the public `widget` API.
- `tests/test_widget.cpp` depends on the same public `widget` API.
- `widget.cpp` depends on `fmt` for formatting and `spdlog` for debug logging.
- Public headers do not expose `fmt` or `spdlog` types, so those dependencies
  can remain implementation details unless the API changes.

## Test Boundary

The current unit test verifies behavior through the public `widget::describe`
function. That keeps tests stable across internal implementation changes while
still checking the behavior used by the executable.

