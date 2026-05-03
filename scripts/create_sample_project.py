#!/usr/bin/env python3
"""Create a starter C++ project matching README.toolchain.md."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


DEFAULT_PROJECT_NAME = "myproject"


def cmake_identifier(value: str) -> str:
    identifier = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not identifier or identifier[0].isdigit():
        identifier = f"project_{identifier}"
    return identifier


def vcpkg_package_name(value: str) -> str:
    name = re.sub(r"[^a-z0-9-]", "-", value.lower())
    name = re.sub(r"-+", "-", name).strip("-")
    return name or DEFAULT_PROJECT_NAME


def render_files(project_name: str) -> dict[Path, str]:
    cmake_name = cmake_identifier(project_name)
    package_name = vcpkg_package_name(project_name)

    vcpkg_manifest = {
        "name": package_name,
        "version-string": "0.1.0",
        "dependencies": [
            "fmt",
            "spdlog",
            {"name": "gtest", "features": []},
        ],
    }

    cmake_presets = {
        "version": 3,
        "cmakeMinimumRequired": {"major": 3, "minor": 22, "patch": 0},
        "configurePresets": [
            {
                "name": "default",
                "displayName": "Default (Ninja, vcpkg)",
                "generator": "Ninja",
                "binaryDir": "${sourceDir}/build/${presetName}",
                "toolchainFile": "$env{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake",
                "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Debug",
                    "CMAKE_EXPORT_COMPILE_COMMANDS": "ON",
                },
            },
            {
                "name": "release",
                "inherits": "default",
                "cacheVariables": {"CMAKE_BUILD_TYPE": "Release"},
            },
        ],
        "buildPresets": [
            {"name": "default", "configurePreset": "default"},
            {"name": "release", "configurePreset": "release"},
        ],
        "testPresets": [
            {
                "name": "default",
                "configurePreset": "default",
                "output": {"outputOnFailure": True},
                "execution": {"noTestsAction": "error", "stopOnFailure": False},
            }
        ],
    }

    return {
        Path(".gitignore"): """build/
vcpkg_installed/
compile_commands.json
.cache/
""",
        Path("vcpkg.json"): json.dumps(vcpkg_manifest, indent=2) + "\n",
        Path("CMakePresets.json"): json.dumps(cmake_presets, indent=2) + "\n",
        Path("CMakeLists.txt"): f"""cmake_minimum_required(VERSION 3.22)

project({cmake_name}
  VERSION 0.1.0
  LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

add_subdirectory(src)

include(CTest)
if(BUILD_TESTING)
  add_subdirectory(tests)
endif()
""",
        Path("src/CMakeLists.txt"): f"""add_library(widget
  lib/widget.cpp
  lib/widget.hpp
)
target_include_directories(widget PUBLIC ${{CMAKE_CURRENT_SOURCE_DIR}}/lib)

find_package(fmt CONFIG REQUIRED)
find_package(spdlog CONFIG REQUIRED)
target_link_libraries(widget PUBLIC fmt::fmt spdlog::spdlog)

add_executable({cmake_name} main.cpp)
target_link_libraries({cmake_name} PRIVATE widget)
""",
        Path("src/main.cpp"): """#include <iostream>

#include "widget.hpp"

int main() {
  std::cout << widget::describe("starter") << '\\n';
  return 0;
}
""",
        Path("src/lib/widget.hpp"): """#pragma once

#include <string>
#include <string_view>

namespace widget {

std::string describe(std::string_view name);

}  // namespace widget
""",
        Path("src/lib/widget.cpp"): """#include "widget.hpp"

#include <string_view>

#include <fmt/format.h>
#include <spdlog/spdlog.h>

namespace widget {

std::string describe(std::string_view name) {
  auto message = fmt::format("widget: {}", name);
  spdlog::debug("created description: {}", message);
  return message;
}

}  // namespace widget
""",
        Path("tests/CMakeLists.txt"): """find_package(GTest CONFIG REQUIRED)

add_executable(test_widget test_widget.cpp)
target_link_libraries(test_widget
  PRIVATE
    widget
    GTest::gtest
    GTest::gtest_main
)

include(GoogleTest)
gtest_discover_tests(test_widget)
""",
        Path("tests/test_widget.cpp"): """#include <gtest/gtest.h>

#include "widget.hpp"

TEST(WidgetTest, DescribesName) {
  EXPECT_EQ(widget::describe("sample"), "widget: sample");
}
""",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a CMake + vcpkg + GoogleTest starter C++ project."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=DEFAULT_PROJECT_NAME,
        help=f"target directory to create (default: {DEFAULT_PROJECT_NAME})",
    )
    parser.add_argument(
        "--name",
        help="CMake project/executable name (default: target directory name)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite files that already exist",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print files that would be created without writing them",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_dir = Path(args.directory).expanduser().resolve()
    project_name = args.name or target_dir.name or DEFAULT_PROJECT_NAME
    files = render_files(project_name)

    existing = [
        target_dir / relative_path
        for relative_path in files
        if (target_dir / relative_path).exists()
    ]
    if existing and not args.force:
        print("Refusing to overwrite existing files. Re-run with --force to replace:", file=sys.stderr)
        for path in existing:
            print(f"  {path}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"Would create project '{project_name}' in {target_dir}:")
        for relative_path in sorted(files):
            print(f"  {relative_path}")
        return 0

    for relative_path, content in files.items():
        path = target_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    print(f"Created sample project '{project_name}' in {target_dir}")
    print("Next steps:")
    print(f"  cd {target_dir}")
    print("  cmake --preset default")
    print("  cmake --build --preset default")
    print("  ctest --preset default")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
