## ADDED Requirements

### Requirement: Project-specific documentation directory
`myproject` SHALL provide a `doc/` directory at `myproject/doc/` for project-specific design documentation.

#### Scenario: Documentation root exists
- **WHEN** the change is implemented
- **THEN** `myproject/doc/` exists
- **AND** the directory contains Markdown documentation for `myproject`

### Requirement: Diagram source directory
`myproject/doc/` SHALL contain an `img_src/` subdirectory for authored diagram source files used by the design documents.

#### Scenario: Diagram source directory exists
- **WHEN** design documents require generated diagrams
- **THEN** editable diagram sources are stored under `myproject/doc/img_src/`
- **AND** PlantUML and Graphviz DOT source files are acceptable source formats

### Requirement: Generated image directory
`myproject/doc/` SHALL contain an `img/` subdirectory for generated images included by Markdown design documents.

#### Scenario: Generated image directory exists
- **WHEN** a Markdown design document includes a generated diagram
- **THEN** the generated image is stored under `myproject/doc/img/`
- **AND** the Markdown document references the image using a relative path from `myproject/doc/`

### Requirement: Source-to-image traceability
Generated documentation images MUST be traceable to their source files by matching base names or by explicit documentation in `myproject/doc/README.md`.

#### Scenario: Matching generated image to source
- **WHEN** a generated image exists in `myproject/doc/img/`
- **THEN** a corresponding source file with the same base name exists in `myproject/doc/img_src/`
- **OR** `myproject/doc/README.md` documents the source relationship explicitly
