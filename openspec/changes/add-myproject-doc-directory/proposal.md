## Why

`myproject` needs a project-specific place for design documentation instead of relying on repo-level setup guides. Design docs should be able to include generated diagrams while keeping the editable diagram sources under version control.

## What Changes

- Add a `myproject/doc/` documentation area for Markdown design documents.
- Add `myproject/doc/img_src/` for authored diagram source files such as PlantUML and Graphviz DOT.
- Add `myproject/doc/img/` for generated image files referenced by Markdown documents.
- Establish naming and linking conventions so generated images can be traced back to their sources.
- Do not change production C++ behavior, build targets, or runtime dependencies.

## Capabilities

### New Capabilities
- `myproject-design-docs`: Defines the required documentation directory structure, Markdown design document conventions, and diagram source/generated image relationship for `myproject`.

### Modified Capabilities

None.

## Impact

- Affected paths: `myproject/doc/`, `myproject/doc/img_src/`, `myproject/doc/img/`.
- No C++ source, CMake, vcpkg, or test behavior changes are expected.
- Generated documentation images may be committed so Markdown docs render without local diagram tooling.
