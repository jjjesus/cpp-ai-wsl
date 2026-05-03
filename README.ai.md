# AI Tooling Setup

Companion to `README.toolchain.md`. Sets up OpenAI Codex, OpenSpec (spec-driven
planning), an `AGENTS.md` for project context, and a small set of project-scoped
Skills for code changes, builds, tests, and static analysis.

The conventions assumed here are those from the toolchain doc: **CMake + vcpkg +
GoogleTest + CTest**, clangd-based LSP, clang-format, clang-tidy. Everything below
lives inside the project repo unless noted otherwise.

## 1. Install OpenAI Codex

Codex is OpenAI's terminal-based agentic coding tool. It runs in WSL2, can edit
files, run commands, and execute tests from inside your repository.

### Prerequisites

Node.js 18+. If you didn't install it as part of the toolchain setup:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node --version    # should be v20.x
```

### Install

```bash
npm install -g @openai/codex
codex --version
```

If `npm install -g` fails with EACCES, configure npm's global prefix to a user
directory rather than using sudo:

```bash
mkdir -p ~/.npm-global
npm config set prefix "$HOME/.npm-global"
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
npm install -g @openai/codex
```

Upgrade later with:

```bash
codex --upgrade
```

### First run and auth

```bash
cd ~/code/myproject
codex --login
codex
```

Choose **Sign in with ChatGPT** when prompted. Current Codex access is included
with ChatGPT Plus, Pro, Business, Enterprise, and Edu plans. Codex can also be
used with API billing; in that setup, export `OPENAI_API_KEY` before launching:

```bash
export OPENAI_API_KEY="<your-key>"
codex
```

If you previously used Codex with an API key and want to switch to ChatGPT plan
access, update Codex, then run:

```bash
codex logout
codex --login
```

### Configuration files

Codex uses these locations:

| Scope         | Location          | Purpose                                        |
|---------------|-------------------|------------------------------------------------|
| User (global) | `~/.codex/`       | Personal config, prompts, credentials, Skills  |
| Project       | `<repo>/.codex/`  | Team Skills and project-scoped agent tooling   |
| Project       | `<repo>/AGENTS.md`| Cross-tool repository context                  |

A useful global `~/.codex/AGENTS.md` or personal instructions file can capture
preferences you want applied across projects:

```markdown
# Personal preferences

- I use Vim/Neovim with clangd. Don't suggest VS Code workflows.
- I prefer modern target-based CMake (3.22+).
- C++20 unless a project specifies otherwise.
- Always run clang-format on edited files before declaring a task done.
- Prefer composition over inheritance, RAII over manual resource management.
- When proposing changes, show the diff, then summarize, then wait for approval.
```

## 2. Install OpenSpec

OpenSpec is a lightweight, brownfield-friendly spec-driven planning layer. It sits
in front of Codex and produces proposals, design notes, and task lists before any
code gets written. Useful when a change is non-trivial and you want to catch
architectural drift on paper rather than in a 500-line wrong PR.

### Install

```bash
npm install -g @fission-ai/openspec
openspec --version
```

Opt out of telemetry (good hygiene generally, required on corporate machines):

```bash
echo 'export OPENSPEC_TELEMETRY=0' >> ~/.bashrc
echo 'export DO_NOT_TRACK=1' >> ~/.bashrc
source ~/.bashrc
```

### Initialize in a project

From the repo root:

```bash
openspec init --tools codex
```

This creates an `openspec/` directory with a `specs/` subtree (the living spec
library) and a `changes/` subtree (in-flight proposals). For Codex, OpenSpec
creates project Skills under `.codex/skills/` and command prompts under
`~/.codex/prompts/` (or `$CODEX_HOME/prompts/` if `CODEX_HOME` is set).

Verify:

```bash
ls -la openspec/
ls -la .codex/skills/
ls -la "${CODEX_HOME:-$HOME/.codex}/prompts/"
```

### Core workflow

Inside a `codex` session, the four commands you use most:

| Command                       | What it does                                                     |
|-------------------------------|------------------------------------------------------------------|
| `/opsx:propose <change-name>` | Generate `proposal.md`, `design.md`, `tasks.md` for a new change |
| `/opsx:apply`                 | Implement the tasks against the spec                             |
| `/opsx:verify`                | Check that the implementation matches the spec                   |
| `/opsx:archive`               | Merge the delta into `openspec/specs/` and clear the change      |

The discipline that makes this useful: **stop after `/opsx:propose` and read the
artifacts before letting the agent code**. That's where OpenSpec earns its keep.

If you want the expanded command set (`/opsx:new`, `/opsx:continue`, `/opsx:ff`,
`/opsx:sync`, `/opsx:bulk-archive`, `/opsx:onboard`):

```bash
openspec config profile      # switch profile interactively
openspec update              # regenerate Codex skill and prompt files
```

The bare CLI also works without an agent -- useful for scripting or CI:

```bash
openspec list                # active changes
openspec show <change>       # change details
openspec validate <change>   # spec format check (--strict for CI)
openspec view                # interactive dashboard
```

## 3. AGENTS.md

`AGENTS.md` at the repo root is the cross-tool convention for "context an AI
agent should load before doing anything." Codex reads it, and so do most other
agents (Claude Code, OpenCode, Cursor, etc.). Keep it short, factual, and
oriented around what the agent needs to make correct decisions -- not what a
human onboarding doc would cover.

Drop this in the repo root as `AGENTS.md`:

```markdown
# Agent context

## Project

C++20 application. Cross-platform target is Linux (WSL2 Ubuntu primary). Built
and tested via CMake + vcpkg + GoogleTest + CTest.

## Toolchain

- Compiler: GCC 11+ or Clang 15+. CI builds with both.
- Build system: CMake 3.22+ with Ninja. Presets in `CMakePresets.json`.
- Dependency manager: vcpkg in manifest mode (`vcpkg.json` at repo root).
  Toolchain file is wired in via the `default` preset; do not pass it manually.
- LSP: clangd. `compile_commands.json` is symlinked at the repo root from
  `build/default/compile_commands.json`.
- Test framework: GoogleTest, registered with CTest via `gtest_discover_tests`.
- Style: clang-format (config in `.clang-format`), clang-tidy (config in
  `.clang-tidy`).

## Layout

- `src/` -- production code. Library targets in `src/lib/`, executable in `src/`.
- `tests/` -- GoogleTest unit tests. One test executable per library target,
  named `test_<target>`.
- `openspec/` -- change proposals and living specs. Read `openspec/specs/` for
  current behavior before proposing changes.
- `build/` -- out-of-source build directories, never committed.

## Commands

Build, test, and run go through the `cmake-build`, `cmake-test`, and
`cmake-run` Skills under `.codex/skills/`. Static analysis goes through the
`clang-tidy-check` Skill. Formatting goes through `clang-format-fix`. Prefer
those over invoking the underlying commands directly so behavior stays
consistent.

## Conventions

- C++20, no exceptions in hot paths, RAII for all resource ownership.
- `target_link_libraries` uses `PUBLIC`/`PRIVATE`/`INTERFACE` explicitly; no bare
  `target_link_libraries(foo bar)` calls.
- New dependencies go through `vcpkg.json` and are linked via `find_package` in
  the appropriate `CMakeLists.txt`. Do not add `FetchContent` for new
  dependencies -- vcpkg is the single dependency manager.
- New unit tests register via `gtest_discover_tests`. Test names use the fixture
  name as the GoogleTest first argument (e.g. `WidgetTest`).
- All edited files must pass clang-format and clang-tidy before a task is
  declared complete.

## Constraints

- Do not modify `CMakePresets.json` without explicit instruction; preset changes
  are a separate, deliberate decision.
- Do not introduce new build systems or dependency managers.
- Do not commit anything from `build/` or `vcpkg_installed/`.
- Do not edit files in `vcpkg_installed/` directly; treat dependency code as
  read-only.

## When stuck

- Read `README.toolchain.md` for build environment details.
- Read `README.ai.md` (this file's companion) for tool setup.
- For non-trivial changes, propose via `/opsx:propose <change-name>` rather than
  editing directly.
```

OpenSpec versions 1.0+ no longer auto-generate `AGENTS.md` -- it's yours to
maintain. That's actually fine; it stays accurate longer when humans write it.

## 4. Project Skills

Skills are project-scoped capability packages that Codex loads on demand. Each is
a directory with a `SKILL.md` plus optional scripts. They live at
`.codex/skills/<skill-name>/SKILL.md` in the repo, get committed to git, and
become available to anyone running `codex` in the project. The frontmatter
`description` is what Codex reads to decide when to invoke the skill, so it
should be specific about the trigger conditions.

Create the directory:

```bash
mkdir -p .codex/skills
```

Then add the skills below. All paths are relative to the repo root.

### `.codex/skills/cmake-build/SKILL.md`

````markdown
---
name: cmake-build
description: Configure and build the project using the standard CMake preset. Use this whenever code has changed and a fresh build is needed, when the user asks to "build", "compile", or "rebuild", or before running tests. Do not invoke cmake or ninja directly; use this skill so the preset, vcpkg toolchain file, and parallelism stay consistent.
---

# Build the project

The project uses CMake presets. The default preset configures a Debug build with
Ninja, vcpkg as the dependency manager, and exports `compile_commands.json` for
clangd.

## Steps

1. If `build/default/` does not exist, configure first:
   ```bash
   cmake --preset default
   ```
2. Build:
   ```bash
   cmake --build --preset default
   ```
3. Refresh the `compile_commands.json` symlink at the repo root if it is missing
   or stale:
   ```bash
   ln -sf build/default/compile_commands.json compile_commands.json
   ```

## Release build

When the user asks for a release or optimized build, swap `default` for `release`
in both commands above.

## Failure handling

- If configure fails on a missing dependency, check `vcpkg.json` first; the
  manifest is the source of truth for dependencies.
- If the build fails with a linker error mentioning a vcpkg target, rerun
  configure -- vcpkg only re-resolves during configure, not during build.
- Do not run `rm -rf build/` to fix problems unless explicitly asked. A stale
  build can usually be repaired with a single reconfigure.
````

### `.codex/skills/cmake-test/SKILL.md`

````markdown
---
name: cmake-test
description: Run the project's unit test suite via CTest. Use this when the user asks to "run tests", "test", or "verify", after code changes that could affect behavior, and as the final step of any task that modifies production code. Do not invoke ctest directly; use this skill so output formatting and failure handling stay consistent.
---

# Run tests

Tests are GoogleTest-based and registered with CTest via `gtest_discover_tests`.
Each `TEST(...)` case appears as an individual CTest entry.

## Steps

1. Ensure the project is built first by running the `cmake-build` skill.
2. Run all tests:
   ```bash
   ctest --preset default
   ```
3. On failure, rerun with verbose output to see GoogleTest diagnostics:
   ```bash
   ctest --preset default --output-on-failure --rerun-failed
   ```

## Filtering tests

To run a subset of tests by name pattern (e.g. one fixture or one case):

```bash
ctest --preset default -R <pattern> --output-on-failure
```

## Reporting results

After running, report:

- Total tests, passed, failed.
- For each failure: the test name, the expected vs. actual values from GoogleTest
  output, and the source location.

Do not mark a code-modification task complete if any test fails. If a test
failure looks unrelated to the change, surface that to the user explicitly rather
than ignoring it or "fixing" it without instruction.
````

### `.codex/skills/cmake-run/SKILL.md`

````markdown
---
name: cmake-run
description: Run the main project executable after building. Use this when the user asks to "run", "launch", or "execute" the program. For test execution, use the cmake-test skill instead.
---

# Run the executable

## Steps

1. Ensure the project is built via the `cmake-build` skill.
2. Locate the executable. Default location is `build/default/src/<project-name>`.
   The project name matches the `project()` declaration in the root
   `CMakeLists.txt`.
3. Run with any arguments the user provided:
   ```bash
   ./build/default/src/<project-name> <args>
   ```

## Sanitizers

If the user asks for a sanitized run (asan, ubsan), reconfigure with the
appropriate flags before running:

```bash
cmake --preset default \
  -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -fno-omit-frame-pointer -g"
cmake --build --preset default
./build/default/src/<project-name> <args>
```
````

### `.codex/skills/clang-format-fix/SKILL.md`

````markdown
---
name: clang-format-fix
description: Apply clang-format to source files. Use this whenever production or test source files (.cpp, .hpp, .h, .cc) have been edited, before declaring an editing task complete. Use it on the specific files that were changed, not on the whole tree, unless the user explicitly asks for a full-tree format pass.
---

# Format edited files

The project uses clang-format with the configuration at `.clang-format`.

## Steps for a targeted format pass

For each file edited in this session:

```bash
clang-format -i --style=file <path-to-file>
```

`--style=file` makes clang-format walk up the directory tree to find
`.clang-format`, which keeps the result consistent regardless of where the file
lives.

## Steps for a full-tree pass

Only when explicitly requested:

```bash
fd -e cpp -e hpp -e h -e cc -X clang-format -i --style=file
```

If `fd` is not on PATH (Ubuntu installs it as `fdfind`), substitute `fdfind`.

## After formatting

Show the user a short summary of which files were touched. Do not show the full
diff unless asked -- clang-format diffs are usually noise.
````

### `.codex/skills/clang-tidy-check/SKILL.md`

````markdown
---
name: clang-tidy-check
description: Run clang-tidy static analysis on edited source files. Use this after non-trivial code changes -- new functions, new files, or anything touching pointers, ownership, or concurrency. Skip for trivial edits like renaming a local variable or fixing a typo. Use it on the specific files that were changed, not on the whole tree.
---

# Static analysis

The project uses clang-tidy. Configuration lives at `.clang-tidy` at the repo
root. clang-tidy reads `compile_commands.json`, so the project must be configured
(via the `cmake-build` skill) before running.

## Steps for a targeted check

For each non-trivially-edited file in this session:

```bash
clang-tidy -p build/default <path-to-file>
```

The `-p` flag points clang-tidy at the build directory containing
`compile_commands.json`.

## Auto-applying fixes

clang-tidy can apply suggested fixes itself, but be conservative -- auto-fix
silently rewrites code, and some checks have false positives. Only apply fixes
when:

- The user explicitly asked, or
- The diagnostics are clearly correct (modernize-* or readability-* checks on
  simple syntactic patterns), and you show the user the diff afterward.

```bash
clang-tidy -p build/default --fix --fix-errors <path-to-file>
```

After auto-fix, run the `clang-format-fix` skill on the same files -- clang-tidy
fixes are not always formatted consistently.

## Reporting results

Group findings by file and severity. For each diagnostic, show:

- The check name (e.g. `modernize-use-nullptr`).
- The file:line:column.
- A one-line summary of the issue.

Do not show the full clang-tidy output verbatim unless asked. It's verbose and
most of it is not actionable.
````

### `.codex/skills/lsp-restart/SKILL.md`

````markdown
---
name: lsp-restart
description: Refresh clangd's view of the project after build system changes. Use this when CMakeLists.txt or vcpkg.json has been modified, after the first configure of a new clone, or when the user reports clangd is showing stale errors or missing includes. Skip for ordinary source-file edits.
---

# Refresh clangd

clangd reads `compile_commands.json` to know how to compile each source file.
When CMake regenerates that file, clangd needs to be told.

## Steps

1. Reconfigure CMake to regenerate `compile_commands.json`:
   ```bash
   cmake --preset default
   ```
2. Refresh the symlink at the repo root if needed:
   ```bash
   ln -sf build/default/compile_commands.json compile_commands.json
   ```
3. Tell the user to restart their LSP. In Neovim that's typically `:LspRestart`
   or `:LspStop` followed by reopening the buffer. Do not try to restart the
   user's editor session from inside Codex.

## When to suspect clangd staleness

- Includes that exist on disk show as "file not found".
- A type or function the user just added shows as undefined.
- Diagnostics reference deleted code.

These all indicate clangd is reading a stale `compile_commands.json` or has
cached an old translation unit. Run this skill before assuming there is an actual
code problem.
````

### `.codex/skills/vcpkg-add-dependency/SKILL.md`

````markdown
---
name: vcpkg-add-dependency
description: Add a new third-party C++ dependency to the project via vcpkg. Use this whenever the user asks to add, install, or pull in a new library. Do not add dependencies via FetchContent, git submodule, or system apt packages -- vcpkg is the single dependency manager for this project.
---

# Add a dependency

The project uses vcpkg in manifest mode. Dependencies are declared in
`vcpkg.json` at the repo root and resolved at CMake configure time.

## Steps

1. Confirm the package name with vcpkg:
   ```bash
   vcpkg search <name>
   ```
   If the search returns multiple ports, ask the user which one they want rather
   than guessing.
2. Add the package to `vcpkg.json` under `dependencies`. Use the bare package name
   unless features are needed:
   ```json
   {
     "dependencies": ["existing-dep", "<new-package>"]
   }
   ```
3. Reconfigure to pull and build the dependency:
   ```bash
   cmake --preset default
   ```
4. Find the correct `find_package` invocation. After the configure step, check
   the usage hint:
   ```bash
   cat vcpkg_installed/*/share/<new-package>/usage 2>/dev/null
   ```
   The usage file shows the exact `find_package` and target names to use.
5. Add `find_package(<Name> CONFIG REQUIRED)` and the appropriate
   `target_link_libraries(... PUBLIC|PRIVATE <Namespace>::<target>)` to the
   relevant `CMakeLists.txt`.
6. Build via the `cmake-build` skill to confirm the dependency links correctly.

## When to use PUBLIC vs PRIVATE

- PUBLIC: the dependency's headers are included in this target's public headers
  (consumers need the dependency too).
- PRIVATE: the dependency is only used in this target's implementation
  (consumers don't need it).
- INTERFACE: header-only consumers, this target doesn't compile anything.

Default to PRIVATE unless headers leak the dependency's types.
````

## 5. Putting it together

A typical session for a non-trivial change:

```text
$ cd ~/code/myproject
$ codex

> /opsx:propose add-rate-limiting
  [Codex generates openspec/changes/add-rate-limiting/{proposal,design,tasks}.md]

# You read the artifacts, edit them directly, refine.

> /opsx:apply
  [Codex implements task by task, invoking cmake-build, cmake-test,
   clang-format-fix, and clang-tidy-check skills as it goes]

> /opsx:verify
  [Codex checks the implementation against the spec]

> /opsx:archive
  [Delta merged into openspec/specs/, change directory cleared]
```

For a trivial edit (rename a variable, fix a typo, add a comment), skip OpenSpec
entirely and ask Codex directly. The proposal flow is overhead that earns its
keep on changes large enough to get wrong.

## 6. What to commit

Commit:

- `AGENTS.md`
- `.codex/skills/` (entire tree)
- `.codex/config.toml` if you add project config that belongs to the team
- `openspec/specs/` (your living spec library)
- `openspec/changes/` is per-change; archived changes get merged into specs and
  cleared, so this is normally empty between changes

Do not commit:

- `~/.codex/` -- that's your personal scope, not the project's
- Codex session transcripts, caches, or credentials

A reasonable `.gitignore` addition:

```gitignore
.codex/sessions/
.codex/cache/
```

## 7. Notes for this environment

**Plan limits.** Heavy agentic sessions on a multi-thousand-file C++ codebase can
hit Codex usage limits faster than short chat use does. If you find yourself
rate-limited mid-task, use a plan with higher Codex limits or API billing.

**WSL2 filesystem.** Keep the repo on the WSL2 filesystem (`~/code/...`), not on
`/mnt/c/...`. Codex does a lot of file I/O during agentic loops, and the 9P bridge
to NTFS will make every operation slow.

**Corporate firewall and proxies.** Codex authenticates to OpenAI services. If
you're behind a TLS-intercepting proxy, set `HTTPS_PROXY`, `HTTP_PROXY`,
`NO_PROXY`, and `SSL_CERT_FILE` (pointing at your org's CA bundle) in your shell
rc before launching. The same variables vcpkg respects.

**Skill iteration.** Adding, editing, or removing a skill under `.codex/skills/`
takes effect when Codex reloads the project context. If Codex does not notice a
new skill immediately, restart the `codex` session from the repo root.
