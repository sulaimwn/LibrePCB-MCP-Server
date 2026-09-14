# Product and implementation specification

## User workflow

The user asks an AI client to inspect a saved project, explain its components and connections, run checks, and show a preview. The server performs explicit, bounded operations and returns results. For a supported edit, it creates a separate candidate copy, validates it, and gives the user a project they can reopen and inspect.

First release is local and Windows-first. Pin one verified stable LibrePCB release. MCP clients and Python versions must be recorded after actual tests. No hosted service, model API integration, live editor attachment, auto-ordering, or cloud deployment is required.

## Proposed architecture

Implementation note (2026-09-11): Days 2–3 implement eight saved-project
inspection/check/export tools on Python 3.12.14, Windows x64, MCP SDK 2.2.0 and
LibrePCB **2.1.1 / file format 2**. Read `docs/DAY2.md` for the inspection subset
and `docs/DAY3.md` for checks, native PNG and fixed PDF/Gerber exports. Day 4
adds an opt-in typed-resistance candidate tool, documented in `docs/DAY4.md`.
Day 5 adds cooperative whole-operation deadlines/cancellation and failure recovery
without expanding the tool set; see `docs/DAY5.md`. Day 6 verifies fresh checkout,
installation and generated-config workflows without expanding domain operations;
see `docs/DAY6.md`. Owner review is pending. General editing and live-editor
control remain planned.

AI client → local MCP server → project adapter and CLI runner → isolated project copies and output artifacts.

- Language: Python. Official MCP SDK 2.2.0 is pinned after checking docs and installed source. Exact Windows/Python 3.12 runtime and build dependencies are hash-locked in `requirements.lock`.
- Separate the MCP transport from domain operations so adapters can be tested without a model.
- The CLI adapter handles supported LibrePCB commands, version detection, timeouts, exit codes, logs and output paths. Pass arguments as an array; never use shell-built commands from model input.
- The project adapter parses S-expressions into a structure, preserves unknown supported content, and resolves identifiers across circuit, schematic, board and embedded library data. Avoid regex replacement for design edits.
- Read the saved state. Label results as a snapshot, never as unsaved GUI state.
- Keep source projects unchanged by default. Candidate copies and generated artifacts live in explicit user-selected/generated working directories.
- Use a process queue initially; serialize operations on a project. Refuse writes to locked/open projects and do not remove another process's lock.
- Record a revision fingerprint before editing and compare it before accepting/applying changes. Reject stale input; do not overwrite newer work.
- Week-one editing produces a new project directory. Replacing the original and multi-file in-place commits are deferred.
- Native C++ integration remains a replaceable future adapter, not a dependency of the first release.

## Proposed MCP tools

The first eight rows are enabled by default. Day 4 implements `create_value_edit`
only with `--enable-experimental-edits`, within the narrow scope below. Lists expose raw template values and typed attributes;
connectivity is limited to circuit signal/component counts.

| Tool | Parameters | Result / scope |
| --- | --- | --- |
| `get_status` | none | Server and LibrePCB versions, supported features, environment problems. |
| `open_project` | `path` | Validated project handle, format version, saved-state revision, lock status, basic metadata. Does not mean opening a GUI window. |
| `get_project_summary` | `project_id` | Boards, schematics, counts, saved snapshot information. |
| `list_components` | `project_id`, optional `cursor`, `limit` | Identifiers, references and values; explicit warnings for unsupported data. |
| `list_nets` | `project_id`, optional `cursor`, `limit` | Net identifiers/names and supported connectivity information. |
| `run_checks` | `project_id`, `checks` = `erc`, `drc`, or `both`; optional `board_id` | Findings, severity, approved/unapproved status where available, tool outcome, raw report artifact. |
| `export_preview` | `project_id`, optional `schematic_id` | All schematic PNG artifacts and one selected native MCP image; first sheet by default. |
| `run_output_job` | `project_id`, `job_name` = `schematic_pdf` or `gerber_excellon`, optional `board_id` | Fixed server-owned job, fresh output directory, verified artifacts and manifest. Board required for multi-board manufacturing. |
| `create_value_edit` *(opt in)* | `project_id`, `component_id`, decimal-string `new_value`, `expected_revision` | Separate typed-resistance candidate path/handle, exact change, CLI strict/save/reopen, file invariants and matching baseline/candidate checks. One board, no unapproved findings; no source replacement. |

Allowlist project roots and output locations. A project ID maps to a validated path inside the server, not arbitrary follow-up paths supplied by the model. Validate identifiers, board selectors, size limits and string length. Do not expose general shell execution or unrestricted Python evaluation as an MCP tool.

## Response contract

Every operation reports success/failure, a readable message and structured details. Include artifact paths when applicable. For long operations, retain raw stdout/stderr separately and return a bounded summary.

Suggested error categories: `unsupported_version`, `project_locked`, `stale_revision`, `invalid_project`, `invalid_argument`, `path_not_allowed`, `cli_missing`, `timeout`, `process_failed`, `validation_failed`.

Rule violations are valid check results, even if the CLI signals them with a nonzero exit code. Confirm exact exit behavior experimentally before mapping it. Unknown/unparseable diagnostics must remain visible rather than being reported as a clean check.

## Editing acceptance

For an existing resistor value change, verify exactly the intended field changes, all UUIDs/references stay intact, component/net counts and connectivity remain equivalent, and existing baseline findings are not hidden. Reopen with the pinned LibrePCB version, save and reopen again, and inspect the generated preview. Demonstrate rollback by discarding the candidate while preserving the source.

## Planned repository layout

Create implementation directories when needed:

```text
src/librepcb_mcp/   transport, domain operations, CLI/project adapters
tests/             meaningful unit and integration tests
tests/fixtures/    small redistributable designs, origins and licenses
docs/              installation, user guide, supported versions
evidence/          concise reports of actual validation runs
work/              ignored scratch copies and generated artifacts
pyproject.toml     package metadata and pinned/locked dependency workflow
```

Do not commit personal board designs, credentials, full user logs, downloaded runtimes, or generated manufacturing outputs by default. Track licenses for reused code and fixtures. The owner authorized uploading this WIP to a private GitHub repository while the server license remains undecided; select a license before a public software release.
