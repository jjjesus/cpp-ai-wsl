## 1. Documentation Structure

- [x] 1.1 Create `myproject/doc/`, `myproject/doc/img_src/`, and `myproject/doc/img/`.
- [x] 1.2 Add `myproject/doc/README.md` describing the documentation purpose, directory layout, image source conventions, generated image conventions, and relative linking rules.
- [x] 1.3 Ensure empty documentation subdirectories are represented in git if no generated assets are added during implementation.

## 2. Initial Design Content

- [x] 2.1 Add at least one project-specific Markdown design document under `myproject/doc/`.
- [x] 2.2 Add at least one editable diagram source file under `myproject/doc/img_src/`, using PlantUML or Graphviz DOT.
- [x] 2.3 Generate the corresponding image under `myproject/doc/img/` with a matching basename where practical.
- [x] 2.4 Reference generated images from Markdown using relative paths from `myproject/doc/`.

## 3. Verification

- [x] 3.1 Verify each generated image in `myproject/doc/img/` has a matching source file in `myproject/doc/img_src/` or an explicit relationship documented in `myproject/doc/README.md`.
- [x] 3.2 Verify Markdown links point to existing files.
- [x] 3.3 Confirm no C++ source, CMake, vcpkg, or test behavior was changed by this documentation-only implementation.
