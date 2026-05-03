## Context

`myproject` is a small C++ starter project under the larger `cpp-ai-wsl` repository. The repo root already contains setup-oriented documentation, but there is no project-local place for design notes about the sample project's structure, build flow, or testing approach.

The requested documentation area is static and file-based. It should be easy to read in a plain Markdown renderer, easy to maintain in git, and able to include diagrams generated from editable text sources.

## Goals / Non-Goals

**Goals:**

- Create a project-local documentation structure under `myproject/doc/`.
- Keep authored design documents as Markdown files.
- Separate editable diagram sources from generated images.
- Make Markdown image references stable and relative.
- Establish conventions that are simple enough to follow manually before automation exists.

**Non-Goals:**

- Do not change C++ production code or tests.
- Do not add new build dependencies to `vcpkg.json`.
- Do not wire diagram generation into the CMake build as part of this change.
- Do not require a specific renderer beyond supporting source files such as PlantUML and Graphviz DOT.

## Decisions

### Decision: Place documentation under `myproject/doc/`

The documentation belongs to the sample project, not the repo-level bootstrap guides. Keeping it under `myproject/doc/` makes the docs portable with the project and avoids mixing project design notes with environment setup documentation.

Alternative considered: root-level `doc/`. This was rejected because root docs currently describe the overall WSL/Codex/OpenSpec setup, while this change is scoped to `myproject`.

### Decision: Use `img_src/` for authored diagram sources

Diagram sources will live in `myproject/doc/img_src/`. This keeps editable PlantUML, Graphviz DOT, or similar text files separate from generated assets while preserving useful diffs in source control.

Alternative considered: colocating diagram source files next to Markdown documents. This was rejected because it makes the documentation root noisier as the number of diagrams grows.

### Decision: Use `img/` for generated images

Generated diagram outputs will live in `myproject/doc/img/` and be referenced by Markdown using relative paths such as `![Build flow](img/build-flow.svg)`.

SVG should be the default generated format when the renderer supports it because it is readable in Markdown viewers, crisp at any size, and generally suitable for diagrams. PNG remains acceptable when a renderer or diagram tool requires it.

Alternative considered: generating images outside the repo. This was rejected because Markdown docs should render for readers without requiring local diagram tooling.

### Decision: Prefer matching basenames between sources and outputs

A source file such as `img_src/build-flow.dot` should generate `img/build-flow.svg`. If a generated image combines multiple sources or uses a non-obvious source, `doc/README.md` should document the relationship.

Alternative considered: relying only on comments inside generated images. This was rejected because generated files are not always readable or preserved by every tool.

## Risks / Trade-offs

- Generated images can drift from source files -> Keep matching basenames and document the render command or source relationship in `doc/README.md`.
- Committing generated images adds duplicate artifacts -> Accept this so Markdown renders without local PlantUML or Graphviz installed.
- Multiple diagram tools may create inconsistent outputs -> Start with conventions and defer strict automation until the docs need it.
- Empty directories are not tracked by git -> Add placeholder files only if needed during implementation.

## Migration Plan

1. Create `myproject/doc/`, `myproject/doc/img_src/`, and `myproject/doc/img/`.
2. Add a `myproject/doc/README.md` that explains the documentation layout and image conventions.
3. Add initial design documents and any initial diagram source/image pairs selected during implementation.
4. Verify Markdown links use relative paths and point to committed files.

Rollback is straightforward: remove the added documentation directory and generated artifacts. No build or runtime behavior is affected.

## Open Questions

- Which initial design documents should be created beyond the documentation index: architecture, build system, testing, or all three?
- Should image rendering be automated now with a script, or deferred until there are enough diagrams to justify it?
