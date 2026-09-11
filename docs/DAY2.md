# Day 2 implementation and handoff details

Historical Day 2 checkpoint. Current checks/export/image behavior is in
[DAY3.md](DAY3.md), with current test results in STATUS and Day 3 evidence.

Implemented September 10, 2026: package `0.1.0.dev2`, Windows x64, Python 3.12.14,
LibrePCB 2.1.1 / stable file format 2, official MCP Python SDK 2.2.0.
This is a local inspection prototype. Day 3 checks and previews remain pending.

## What exists

| Registered tool | Actual behavior |
| --- | --- |
| `get_status()` | Runs the real CLI version command, checks the supported version, reports readiness, tools and limits. A missing binary returns `ok: true` with `ready: false` and a structured problem. |
| `open_project(path)` | Accepts an absolute extracted `.lpp` path inside configured roots. Captures a closed saved design, parses the supported subset, validates an isolated copy with the real CLI, verifies source/copy hashes, and returns a session handle and summary. Does not open the GUI. |
| `get_project_summary(project_id)` | Rechecks saved revisions and lock/recovery state, then returns metadata, board/schematic indexes and component/net counts. |
| `list_components(project_id, cursor=None, limit=50)` | Paginates component UUIDs, references, raw values, typed attributes, embedded library component IDs and signal counts. |
| `list_nets(project_id, cursor=None, limit=50)` | Paginates net UUIDs, names, net-class IDs, assigned signal counts and distinct connected component counts. |

No `run_checks`, preview/export, output-job, edit, arbitrary shell or Python tool
is registered. Day 1 demonstrates CLI check/export feasibility only.

## Boundaries in code

- `server.py`: STDIO transport, typed tool signatures, MCP annotations and bounded
  text plus structured responses. Calls the domain service in a worker thread.
- `service.py`: serialized operations, configured roots, session handles,
  revisions, fixed CLI operations, pagination and error translation.
- `adapters/files.py`: bounded saved-file capture, local path restrictions,
  Windows link/junction rejection, locks/recovery and byte-preserving copies.
- `adapters/sexpr.py`: read-only recursive S-expression parser with original
  spans, strings/escapes, tokens, lists, comments and complexity bounds. No eval,
  regex rewriting or serializer.
- `adapters/project.py`: documented format-2 projection plus identifier and
  relationship checks. LibrePCB subsequently validates the full saved design.
- `adapters/cli.py`: trusted argument-array subprocess adapter retained from Day 1.

SDK v2 uses `from mcp.server import MCPServer` and
`from mcp import Client, StdioServerParameters, stdio_client`. The tested client
is `Client(stdio_client(parameters), mode="legacy")`; automatic mode also works.
Do not replace this with remembered v1 FastMCP imports without checking the pin.
Tools return `CallToolResult` with `structured_content` and matching `is_error`.
The SDK infers input schemas; these tools do not advertise an output schema.

## Supported saved-file projection

The reader requires `.librepcb-project` equal to `2`, the `.lpp` marker, project
metadata, circuit data, schematic/board indexes and their referenced documents,
and embedded component library data. UUIDs must be canonical and unique within
their collections. Component names and net names must be unique. Net classes,
component variants, assigned signal sets and projected page/component references
must resolve. Unsupported circuit/component/net/index shapes fail explicitly.

Unknown content in the accepted projection's other documents is retained in the
byte-identical snapshot. The reader does not rewrite any design document. This
is not a general-purpose LibrePCB serializer or a complete geometry parser.
Board geometry, wires, traces, devices/packages, assembly variants and display
value evaluation are not exposed as inspected data; real CLI opening is the
additional full-project validation gate.

Fixture facts: 97 components, 48 circuit nets, one board and two schematic sheets
(`Main`, `Ethernet`). R17 has raw value `{{RESISTANCE}}` and typed attribute
`RESISTANCE / resistance / kiloohm / 1.5`. GND has 58 assigned signals from 50
distinct components. The raw template is not the resolved display value.

## Consistency, paths and limits

Only local absolute paths are accepted. Configured roots must exist. UNC/device
paths, parent traversal, alternate data streams, symlinks, junctions/reparse
points and hardlinked project files are unsupported. Sources and server data
directories must not overlap. Internal document paths must be normalized relative
paths without traversal. Root membership uses path containment, not a string prefix.

Any `.lock`, `.autosave` or `.backup` entry rejects inspection. Recovery belongs
in LibrePCB; the server never deletes these entries. Read results always say
`saved_snapshot`, never unsaved GUI state. Source and copy revisions are checked
after opening and before every subsequent inspection. Any changed file requires
opening a new handle; handles expire with the server process. SHA256 fingerprints
cover relative paths and contents, excluding VCS directories `.git`, `.hg`, `.svn`.

These checks assume a cooperative local filesystem. They do not provide an
atomic transaction against an adversarial process swapping files between checks.
They also deliberately reject an otherwise readable project with a lock present.

| Limit | Value |
| --- | --- |
| Files plus directories visited | 5,000 |
| Individual file / total captured bytes | 16 MB / 100 MB (decimal) |
| Parser depth / nodes / string characters | 64 / 250,000 / 65,536 |
| Components / nets / pages per kind | 5,000 / 10,000 / 32 |
| Page request | 1–100 items; also capped by encoded record bytes |
| Serialized tool response | 64,000 bytes; text and structured copies included |
| Snapshot attempts after validation | 32 per server session |
| CLI timeout | 30 seconds by default, configurable up to 300 |

Raw CLI diagnostics are separate files with 4,000-byte excerpts at the adapter
boundary. Raw logs and retained snapshots have no disk-retention policy yet.
Each session uses a unique data directory and never replaces a prior snapshot.
Paths for generated copies must remain below this Windows setup's 260-character
limit. Use a short `--data-root` if `path_too_long` is returned; no system setting
was changed to enable long paths. The test/demo harnesses use short run names.

## Actual client verification

`scripts/verify_mcp.py` launches real STDIO subprocesses through SDK 2.2.0. Both
legacy initialize (`2025-11-25`) and automatic discovery (`2026-07-28`) work.
It checks every tool, complete component/net pagination, bounded responses,
error flags, raw values, source and snapshot preservation, containment, lock and
recovery rejection, changed source/copy revisions, invalid files, missing device
data rejected by the real CLI, missing CLI, and session-scoped handles.

`scripts/verify_codex_host.py` uses the installed `codex-cli 0.153.4` app-server
JSON-RPC interfaces verified through its generated local schemas. It starts an
ephemeral thread and calls all five tools via `mcpServer/tool/call`, then verifies
a structured rejection. It starts no model turn or second coding agent. This is
an actual Codex host test, not a graphical UI interaction or a Claude test.
Process-local overrides disable unrelated plugins/apps; host settings and login
files are not modified. All harness-owned processes are stopped on completion.

The hash-locked dependencies and editable package were also installed in a fresh
`work/v2` venv, where the final SDK integration and unit tests ran. Fresh-machine
installation, Claude connection, graphical rendering and an owner-followed trial
are still unverified. See the Day 2 evidence directory for exact results.

## Sources checked before implementation

- [Official SDK v2.2.0 source](https://github.com/modelcontextprotocol/python-sdk/tree/v2.2.0),
  commit `9972c21aa42054fb1450c5fc614761ed11847ec6`; installed source/signatures also inspected.
- [SDK client transports at the pinned tag](https://github.com/modelcontextprotocol/python-sdk/blob/v2.2.0/docs/client/transports.md).
- [Pinned LibrePCB S-expression implementation](https://github.com/LibrePCB/LibrePCB/blob/2.1.1/libs/librepcb/core/serialization/sexpression.cpp).
- [Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).
- [Official SDK host connection guide](https://py.sdk.modelcontextprotocol.io/get-started/real-host/).
