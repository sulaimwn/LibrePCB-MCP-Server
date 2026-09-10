# Product and implementation specification

## User workflow

The user asks an AI client to inspect a saved project, explain its components and connections, run checks, and show a preview. The server performs explicit, bounded operations and returns results. For a supported edit, it creates a separate candidate copy, validates it, and gives the user a project they can reopen and inspect.

First release is local and Windows-first. Pin one verified stable LibrePCB release. MCP clients and Python versions must be recorded after actual tests. No hosted service, model API integration, live editor attachment, auto-ordering, or cloud deployment is required.

## Proposed architecture

AI client → local MCP server → project adapter and CLI runner → isolated project copies and output artifacts.

- Preferred starting language: Python, because the initial work is process orchestration and structured text parsing. Select and pin a maintained official MCP Python SDK version after checking its current documentation on Day 2. Do not invent imports from memory.
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

These names and parameters are a design proposal, not implemented capabilities. Return structured data; distinguish proposed tools in docs from actual registered tools.

| Tool | Parameters | Result / scope |
| --- | --- | --- |
| `get_status` | none | Server and LibrePCB versions, supported features, environment problems. |
| `open_project` | `path` | Validated project handle, format version, saved-state revision, lock status, basic metadata. Does not mean opening a GUI window. |
| `get_project_summary` | `project_id` | Boards, schematics, counts, saved snapshot information. |
| `list_components` | `project_id`, optional `cursor`, `limit` | Identifiers, references and values; explicit warnings for unsupported data. |
| `list_nets` | `project_id`, optional `cursor`, `limit` | Net identifiers/names and supported connectivity information. |
| `run_checks` | `project_id`, `checks` = `erc`, `drc`, or `both`; optional board selector | Findings, severity, approved/unapproved status where available, tool outcome, raw report artifact. |
| `export_preview` | `project_id`, supported target/board selector | Preview artifact from a verified output job. Prefer bounded PNG for model inspection; capability depends on the pinned CLI/client. |
| `run_output_job` | `project_id`, validated configured `job_name` | Generated artifacts within the designated export directory. Initially support a small known set of job types. |
| `create_value_edit` | `project_id`, `component_id`, `new_value`, `expected_revision` | Candidate project path, changed-value summary and validation results. Only if Day 4 passes. |

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

Do not commit personal board designs, credentials, full user logs, downloaded runtimes, or generated manufacturing outputs by default. Choose the project license before external distribution and track licenses for reused code and fixtures.
