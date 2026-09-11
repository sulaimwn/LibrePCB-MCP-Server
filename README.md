# LibrePCB-MCP-Server

> **WIP — experimental software under active development.** Interfaces and supported
> behavior may change. This is not a finished product or an official LibrePCB integration.

A local MCP server that lets a compatible AI client inspect saved LibrePCB projects,
run electrical and board-rule checks, view schematic previews, and export PDF and
manufacturing files. It works on isolated copies and preserves the source design.

The current prototype targets **Windows x64, Python 3.12 and LibrePCB 2.1.1**.
It uses the official **MCP Python SDK 2.2.0** over STDIO. The server makes no model
API calls and needs no subscription credentials or model API keys.

## What works today

| Tool | Current behavior |
| --- | --- |
| `get_status` | Reports the server/LibrePCB versions, readiness and supported operations. |
| `open_project` | Validates an allowed, closed `.lpp` project and creates a saved snapshot. |
| `get_project_summary` | Returns project metadata, boards, schematic sheets and counts. |
| `list_components` | Lists references, raw values, typed attributes and signal counts, with pagination. |
| `list_nets` | Lists circuit nets and connected signal/component counts, with pagination. |
| `run_checks` | Runs real ERC/DRC and separates approved findings, unapproved findings and check failures. |
| `export_preview` | Exports schematic PNGs and attaches one selected sheet as a native MCP image. |
| `run_output_job` | Runs a server-owned schematic PDF or Gerber/Excellon job in a new output directory. |

Checks and exports use the pinned LibrePCB CLI. A rule violation is a valid check
result; missing, contradictory or unfamiliar diagnostics are never treated as a
pass. Exports use fixed server-owned jobs and filenames, and return artifact paths,
hashes and raw diagnostic paths.

**Not implemented yet:** design-edit tools, component placement, wiring, routing,
live access to unsaved GUI state, general library authoring, and support for other
operating systems or LibrePCB releases. The next milestone is one constrained
value-edit experiment, subject to validation and rollback gates.

## Example workflow

After connecting the server, ask your MCP client:

> Open my saved LibrePCB project, summarize its components and nets, run ERC and
> DRC, and show the Main schematic. Report approved and unapproved findings
> separately, then export the schematic PDF.

The client opens the absolute `.lpp` path and uses the returned project handle for
subsequent tools. For multi-board projects, select a board explicitly for DRC and
manufacturing exports. Component values may be templates such as `{{RESISTANCE}}`;
the reader exposes the separate typed attributes instead of guessing the display value.

![Actual MCP schematic preview of the D0 reader Ethernet sheet](docs/images/d0-reader-ethernet.png)

*Real LibrePCB output received through MCP, using the included CC0 D0 reader
sample by U. Bruhin. This is a compatibility example, not a manufacturing approval.*

## Windows quickstart

Install Python **3.12 x64**, clone this repository, and run from its folder in PowerShell:

```powershell
.\scripts\bootstrap.ps1 -PythonExe python
.\.venv\Scripts\python.exe scripts\prepare_demo.py
```

`python` must resolve to a real Python 3.12 interpreter. You can pass its absolute
path instead. The bootstrap downloads the pinned portable LibrePCB build, checks
its hash/signature, and installs the hash-locked Python dependencies and local package.

The demo command creates a fresh sample plus **Codex TOML**, **Claude Desktop JSON**
and a sample prompt under `work/demo-<id>/`. Merge the relevant server entry into
your client's configuration, preserving existing entries. The script generates
snippets only; it does not modify client settings. The client starts the STDIO
server when needed.

See [Windows setup](docs/WINDOWS_SETUP.md) for complete commands, configuration and
troubleshooting. Codex host tool calls and native image delivery have been tested;
Claude connection and an owner-followed installation trial are still pending.

## Current validation

The included real sample has **97 components, 48 nets, one board and two schematic
sheets**. Its baseline retains 2 approved ERC findings and 16 approved DRC findings,
with no unapproved findings. Tests also introduce a disconnected net and a trace
below the board's minimum width, then verify LibrePCB reports the new faults.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts\verify_mcp.py
.\.venv\Scripts\python.exe scripts\verify_day3.py
```

Recorded results: **33 unit/adapter tests**, **82 inspection MCP checks**, **73
check/export/image MCP checks**, and **12 installed Codex host checks** passed.
All 184 source-fixture files remained unchanged. The generated schematic images
were also visually inspected. See [Day 3 evidence](evidence/2026-09-11-day3/README.md)
for exact runs, failures resolved and the limits of these claims.

These results do not establish electrical correctness, production readiness or
compatibility with arbitrary designs. GUI save/reopen, editing/rollback, a personal
project trial and fresh-machine installation remain later acceptance work.

## Working boundaries

- Closed, saved projects under explicitly configured local roots.
- Lock/recovery entries, stale revisions, linked paths and unsupported formats are rejected.
- New directories for exports; existing output is never silently overwritten.
- Bounded tool results, preview image sizes, parser work and retained CLI logs.
- No arbitrary shell, Python, caller-selected output paths or project-job execution.
- Retained snapshots/artifacts still need manual cleanup between inactive sessions.

Implementation details and exact limits are in [Day 3 notes](docs/DAY3.md) and
[Day 2 inspection notes](docs/DAY2.md).

## Project context and roadmap

- [STATUS.md](STATUS.md): current implementation, real tests and next task.
- [PLAN.md](PLAN.md): milestone plan and release gates.
- [SPEC.md](SPEC.md): implemented versus proposed interfaces.
- [HANDOFF.md](HANDOFF.md): context for continuing in another coding client.
- [RESEARCH.md](RESEARCH.md): verified sources and historical design references.

The repository preserves source, documentation, fixture, test evidence and project
history. Downloaded runtimes, virtual environments, temporary work and credentials
are excluded and can be recreated from the setup instructions.

## License and attribution

A software license for the server has not yet been chosen. The included D0 reader
fixture is **CC0-1.0**; see [fixture provenance](tests/fixtures/README.md). LibrePCB
and other dependencies retain their own licenses and are not bundled into this repository.
