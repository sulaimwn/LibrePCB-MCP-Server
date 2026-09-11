# Day 3: checks, previews and fixed exports

Implemented and verified September 11, 2026. Package `0.1.0.dev3`, Windows x64,
Python 3.12.14, official MCP SDK 2.2.0, LibrePCB 2.1.1 / stable format 2.
The project remains WIP. Day 2 inspection behavior is documented in `DAY2.md`.

## New tools

| Tool | Inputs | Behavior |
| --- | --- | --- |
| `run_checks` | `project_id`, `checks="erc"`, `"drc"` or `"both"` (default), optional `board_id` | Runs ERC and/or DRC on the validated saved copy. For multiple boards, DRC requires a board ID. ERC is circuit-wide and does not accept one. |
| `export_preview` | `project_id`, optional `schematic_id` | Exports every schematic as a PNG, lists the artifacts and attaches one selected sheet as a native MCP image. The first sheet is selected by default. |
| `run_output_job` | `project_id`, `job_name="schematic_pdf"` or `"gerber_excellon"`, optional `board_id` | Runs a server-owned PDF or manufacturing job. Manufacturing requires a board ID for multi-board designs. No caller output paths or arbitrary job names. |

There are eight tools in total. No design-edit tool exists. The two export tools
have `readOnlyHint=false` because they create artifacts, and
`destructiveHint=false` because they never overwrite existing output. Existing
source-project preservation rules remain in force.

## Rule-check results

ERC and each selected board's DRC use separate CLI invocations. This avoids
guessing which check or board produced a finding when stdout and stderr are
separate streams. Board selection uses a validated UUID mapped to the CLI's
numeric `--board-index` argument; a board name is never a shell command.

For an interpreted run, `ok=true` and the data contains:

- `outcome`: `passed` or `violations`.
- Approved and unapproved totals, plus per-check counts and board metadata.
- Up to 50 finding details per check, further bounded by 6,000 encoded JSON
  bytes. Findings include severity, message and `approved=false`.
- `findings_truncated`, raw stdout/stderr artifact paths and a JSON report path.
- Saved-state label, project handle and revision.

A design violation is a successful check operation with `outcome=violations`,
not a process crash. `passed` means the requested check completed with no
unapproved findings; approved findings remain present. LibrePCB's CLI reports
their count but not their individual details, so `approval_details_available=false`.

The parser requires the expected opening/check/board lines, counts, completion
marker, exit code and matching number of stderr findings. Unknown diagnostics,
fatal stderr, unexpected stdout, missing completion, contradictory counts or
unknown severities make the check **indeterminate**. The service returns an MCP
error with `check_failed` (or the process failure category) and raw/report paths.
It never converts an unrecognized diagnostic stream into a clean result.

English output on the recorded Windows environment is the tested format. A
localized or changed format should fail conservatively until explicitly supported.

## Export boundary and artifacts

The package includes `resources/preview.lp` and `resources/gerber.lp`. The preview
template is derived from the verified Day 1 job and fixes paper size to A4 at
150 DPI. PDF uses the same server-owned schematic content with a fixed PDF
filename. Gerber/Excellon uses a validated board UUID and a static `gerber/board`
basename. The only filename substitutions are CLI-generated layer numbers.
Project/variant names and other design attributes never determine export paths.

The CLI always receives an explicit server-owned `--jobs` file and a new
`--outdir`; the project's jobs are not executed. Each operation creates a fresh
directory under the configured data root. An existing directory, including a
preoccupied operation path, is rejected rather than overwritten.

LibrePCB writes a `.librepcb-output` control file beside its deliverables. The
adapter verifies its relative paths, exact job UUID and correspondence to the
actual files, then excludes it from the deliverable list. Unknown extra files,
linked output, escaping paths, incorrect page counts and invalid file headers fail.

Each artifact has an opaque ID, absolute path, filename, media type, byte count
and SHA256. PNGs also include dimensions. An `artifacts.json` manifest and raw
CLI logs remain alongside the export. The preview image is rehashed before the
transport attaches its bytes; changed artifacts fail with `stale_revision`.

Exports are compatibility outputs, not manufacturing approval. They do not
silently run or approve rule checks; the normal client workflow calls checks first.

## New limits and retained limitations

| Boundary | Limit |
| --- | --- |
| Check/export operations per server session | 64, including failed attempts after allocation |
| Retained stdout/stderr | 2,000,000 bytes per stream; process stopped when cap is reached |
| Diagnostic excerpts | 4,000 bytes per stream |
| Ordinary serialized tool result | 64,000 bytes including text/structured duplication |
| Native PNG | 1,000,000 bytes, width/height at most 2,500 pixels |
| Tool response including one PNG | 1,500,000 serialized bytes |
| Deliverables per export / total deliverable size | 64 / 32 MB |
| Output control manifest | 16,384 bytes |

File count/size checks apply to completed exports; they are not an OS filesystem
quota during rendering. The jobs have fixed supported outputs and PNG page bounds.
The process adapter caps retained diagnostic files while draining both streams,
and reports `output_limit` rather than claiming complete diagnostics.

CLI timeout remains per invocation (30 seconds by default). A combined operation
can run version detection plus ERC and DRC; generated Codex config now allows
120 seconds per tool. CLI settings up to 300 seconds require a correspondingly
longer host timeout. Raw logs/copies/artifacts remain until manually cleaned up
while their sessions are inactive; automatic retention is not implemented.

Source and snapshot locks/recovery/revisions are rechecked before and after CLI
work. These checks preserve saved state in cooperative local use, not an atomic
transaction against an adversarial filesystem writer. General geometry parsing,
display-template evaluation, GUI state and edit serialization remain unsupported.

## Evidence and actual host coverage

`scripts/verify_day3.py` exercises actual STDIO MCP calls and the pinned CLI.
It verifies the clean baseline; a new unconnected circuit net; an existing trace
narrowed from 0.2 mm to 0.01 mm; native PNG responses for both sheets; PDF and
11 Gerber/drill artifacts; manifest/hash/path checks; repeated exports; occupied
output paths; rejected project job execution; unknown selectors; and lock rejection.
The original fixture and all test-source copies are preserved during MCP calls.

`scripts/verify_codex_host.py` now calls all eight tools through the installed
Codex 0.153.4 app-server. It receives a native PNG, decodes and hashes its actual
bytes, and verifies checks, PDF and manufacturing exports. This agent visually
inspected the received Main image and the SDK-received Ethernet image. The image
in the root README is an unchanged copy of the latter.

This uses an ephemeral Codex host thread and direct tool calls, not a model turn,
UI click-through or persistent client installation. It does prove that the host
passes through usable image bytes and that this agent can inspect them. Claude
connection, personal designs, GUI save/reopen and an owner trial remain untested.

The wheel includes the job resources. The packaged server was also installed in
the existing isolated `work/v2` environment for a full Day 3 MCP run. This is a
packaged-server test, not a fresh-machine installation trial or published release.
See `evidence/2026-09-11-day3/` for exact results and paths.

## Verified sources

- [LibrePCB CLI documentation](https://librepcb.org/docs/cli/open-project/), also checked against the actual local `--help` and executions.
- [Pinned CLI diagnostic formatting](https://github.com/LibrePCB/LibrePCB/blob/2.1.1/apps/librepcb-cli/commandlineinterface.cpp).
- [Pinned electrical rule checker](https://github.com/LibrePCB/LibrePCB/blob/2.1.1/libs/librepcb/core/project/erc/electricalrulecheck.cpp).
- [Pinned output-job object/board selection](https://github.com/LibrePCB/LibrePCB/blob/2.1.1/libs/librepcb/core/job/outputjob.h).
- [Pinned graphics job](https://github.com/LibrePCB/LibrePCB/blob/2.1.1/libs/librepcb/core/job/graphicsoutputjob.cpp) and [Gerber/Excellon job](https://github.com/LibrePCB/LibrePCB/blob/2.1.1/libs/librepcb/core/job/gerberexcellonoutputjob.cpp).
- `ImageContent`, `CallToolResult` and Codex app-server schemas were checked against the installed SDK/host interfaces before use.
