# C++ Toolchain Setup (WSL2 Ubuntu)

Setup guide for a terminal-first C++ development environment using **CMake + vcpkg + GoogleTest +
CTest** on WSL2 Ubuntu. No IDE required; works with Vim/Neovim and clangd.

## 1. Prerequisites

Assumes WSL2 with Ubuntu 22.04 LTS or newer.

```bash
sudo apt update && sudo apt upgrade -y
```

## 2. Base toolchain

Install compilers, build tools, and useful CLI utilities:

```bash
sudo apt install -y \
  build-essential gdb cmake ninja-build pkg-config \
  clang clangd clang-format clang-tidy lld lldb \
  git curl zip unzip tar wget \
  ripgrep fd-find universal-ctags \
  python3 python3-pip \
  autoconf automake libtool m4
```

The `zip`/`unzip`/`tar`/`curl` packages are required by vcpkg for fetching and unpacking ports. The
autotools packages (`autoconf`, `automake`, `libtool`) are needed because some vcpkg ports build
with autotools.

Symlink `fdfind` to `fd` (Ubuntu naming quirk):

```bash
mkdir -p ~/.local/bin
ln -sf "$(which fdfind)" ~/.local/bin/fd
```

Verify versions:

```bash
gcc --version       # should be 11+ on 22.04, 13+ on 24.04
cmake --version     # should be 3.22+
ninja --version
clangd --version
```

If you need a newer CMake than apt provides, Kitware maintains an apt repo at `apt.kitware.com`. If
you need newer GCC, the `ubuntu-toolchain-r/test` PPA has it. For newer Clang, see `apt.llvm.org`.

## 3. Install vcpkg

Install to your home directory; do **not** use sudo.

```bash
git clone https://github.com/microsoft/vcpkg.git ~/vcpkg
cd ~/vcpkg
./bootstrap-vcpkg.sh -disableMetrics
```

Add to your shell rc (`~/.bashrc` or `~/.zshrc`):

```bash
export VCPKG_ROOT="$HOME/vcpkg"
export PATH="$VCPKG_ROOT:$PATH"
```

Reload your shell (`source ~/.bashrc`) and verify:

```bash
vcpkg version
```

### Behind a corporate firewall

If you're on a network with TLS interception or a proxy, vcpkg needs to be told. Common variables:

```bash
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"
export NO_PROXY="localhost,127.0.0.1"
# If your org uses a custom CA bundle:
export SSL_CERT_FILE="/etc/ssl/certs/ca-certificates.crt"
```

For mirrored/internal binary caches, set `VCPKG_BINARY_SOURCES` per the vcpkg docs.

## 4. Project layout

A clean starter project:

```
myproject/
+-- CMakeLists.txt
+-- CMakePresets.json
+-- vcpkg.json
+-- .gitignore
+-- src/
|   +-- CMakeLists.txt
|   +-- main.cpp
|   +-- lib/
|       +-- widget.cpp
|       +-- widget.hpp
+-- tests/
    +-- CMakeLists.txt
    +-- test_widget.cpp
```

### `vcpkg.json` (manifest mode)

Declares dependencies per-project. vcpkg installs them to a project-local `vcpkg_installed/`
directory at configure time.

```json
{
  "name": "myproject",
  "version-string": "0.1.0",
  "dependencies": [
    "fmt",
    "spdlog",
    {
      "name": "gtest",
      "features": []
    }
  ]
}
```

### `CMakeLists.txt` (root)

```cmake
cmake_minimum_required(VERSION 3.22)

project(myproject
  VERSION 0.1.0
  LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Always emit compile_commands.json for clangd
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Reasonable warning defaults
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

add_subdirectory(src)

include(CTest)
if(BUILD_TESTING)
  add_subdirectory(tests)
endif()
```

### `src/CMakeLists.txt`

```cmake
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
```

### `tests/CMakeLists.txt`

```cmake
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
```

`gtest_discover_tests` registers each `TEST(...)` case with CTest individually, so `ctest -V` shows
per-test results and you can filter with `ctest -R PatternName`.

### `tests/test_widget.cpp`

```cpp
#include <gtest/gtest.h>
#include "widget.hpp"

TEST(WidgetTest, BasicSanity) {
  EXPECT_EQ(2 + 2, 4);
}
```

### `CMakePresets.json`

Presets give you named build configurations and remove the need to remember toolchain-file paths.
Note the `$env{VCPKG_ROOT}` reference -- it pulls from the env var you set earlier.

```json
{
  "version": 3,
  "cmakeMinimumRequired": { "major": 3, "minor": 22, "patch": 0 },
  "configurePresets": [
    {
      "name": "default",
      "displayName": "Default (Ninja, vcpkg)",
      "generator": "Ninja",
      "binaryDir": "${sourceDir}/build/${presetName}",
      "toolchainFile": "$env{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake",
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug",
        "CMAKE_EXPORT_COMPILE_COMMANDS": "ON"
      }
    },
    {
      "name": "release",
      "inherits": "default",
      "cacheVariables": { "CMAKE_BUILD_TYPE": "Release" }
    }
  ],
  "buildPresets": [
    { "name": "default", "configurePreset": "default" },
    { "name": "release", "configurePreset": "release" }
  ],
  "testPresets": [
    {
      "name": "default",
      "configurePreset": "default",
      "output": { "outputOnFailure": true },
      "execution": { "noTestsAction": "error", "stopOnFailure": false }
    }
  ]
}
```

### `.gitignore`

```
build/
vcpkg_installed/
compile_commands.json
.cache/
```

## 5. Build, test, run

From the project root:

```bash
# Configure (first time, or after CMakeLists changes)
cmake --preset default

# Build
cmake --build --preset default

# Test
ctest --preset default

# Run
./build/default/src/myproject
```

For release builds, swap `default` for `release`.

## 6. clangd integration

clangd needs `compile_commands.json` at the project root. CMake puts it in the build directory;
symlink it up:

```bash
ln -sf build/default/compile_commands.json compile_commands.json
```

Add a `.clangd` file at the project root for tweaks (optional):

```yaml
CompileFlags:
  Add: [-Wall, -Wextra]
Diagnostics:
  UnusedIncludes: Strict
  ClangTidy:
    Add: [modernize-*, performance-*, readability-*]
    Remove: [modernize-use-trailing-return-type]
```

In Vim/Neovim, point your LSP client at the `clangd` binary on `$PATH`. Restart the LSP after the
first configure so it picks up `compile_commands.json`.

## 7. Adding a dependency

Edit `vcpkg.json`, add the package name (find it via `vcpkg search <name>`), then re-run configure:

```bash
cmake --preset default
```

vcpkg fetches and builds the dependency on the next configure. In `CMakeLists.txt`, find and link
it:

```cmake
find_package(nlohmann_json CONFIG REQUIRED)
target_link_libraries(widget PUBLIC nlohmann_json::nlohmann_json)
```

The exact `find_package` name and target name are listed in vcpkg's per-port usage notes; check
`vcpkg_installed/<triplet>/share/<port>/usage` after install, or run `vcpkg install <port>` once
interactively to see the usage hint.

## 8. Common workflow notes

**Filesystem performance.** Keep your project on the WSL2 filesystem (`~/code/...`), not on
`/mnt/c/...`. Cross-filesystem I/O through the 9P bridge is dramatically slower and will make CMake
configure times miserable.

**Reconfigure when changing `vcpkg.json`.** vcpkg only re-resolves dependencies during CMake
configure, not during build. Edit the manifest, then re-run `cmake --preset default`.

**Clean rebuild.** Delete the build directory: `rm -rf build/default && cmake --preset default`.
Don't delete `vcpkg_installed/` unless you want to rebuild every dependency from source.

**Parallel builds.** Ninja parallelizes by default. To cap jobs (useful on memory-constrained
builds): `cmake --build --preset default -- -j 4`.

**Sanitizers during development.** Add to your debug preset's cache variables, or pass on the
command line:

```bash
cmake --preset default \
  -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -fno-omit-frame-pointer"
```

**Filter tests.** `ctest --preset default -R WidgetTest` runs only matching test names. `ctest
--preset default --output-on-failure` is what you usually want.

## 9. What this gets you

- Reproducible builds with declared dependencies in `vcpkg.json`.
- A single configure command (`cmake --preset default`) regardless of platform.
- `compile_commands.json` for clangd, so completion, go-to-definition, and diagnostics work in
- Vim/Neovim out of the box.
- Per-test CTest registration via `gtest_discover_tests` so test failures are visible at the
- test-case level, not just the executable level.
- Standard layout that other C++ developers will recognize without explanation.
