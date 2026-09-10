# Day 2 recorded validation

Date: 2026-09-10. Coding client: ChatGPT/Codex. Package `0.1.0.dev2`.
See `docs/DAY2.md` for implementation details and known limits.

## Passing runs

| Check | Actual outcome |
| --- | --- |
| `work/v2/Scripts/python.exe scripts/verify_mcp.py` | **82 checks passed, 27 tool calls**, real SDK STDIO subprocesses and LibrePCB 2.1.1. |
| `.venv/Scripts/python.exe scripts/verify_codex_host.py --codex <recorded executable>` | **7 checks passed**, all five tools plus a structured rejection through installed Codex 0.153.4's app-server host. |
| `work/v2/Scripts/python.exe -m unittest discover -s tests -v` | **19 tests passed** in 21.146 seconds: 6 process tests, 4 parser tests, 9 real-fixture/path tests, including a real Windows junction. |
| Fresh `work/v2` installation | 36 exact dependencies installed with `--require-hashes`; editable package built/installed with no dependency resolution or build isolation; `pip check` passed. |
| Updated `scripts/bootstrap.ps1` | Passed with the existing portable LibrePCB and `.venv`; installs locked dependencies and editable package. |
| `scripts/prepare_demo.py` | Created `work/demo-bf2ee7` sample, valid TOML and JSON client snippets and sample prompt. No client settings changed. |

SDK integration run: `work/d2-2767e3/`. Codex host run: `work/cx-5134f6/`.
SDK legacy protocol was **2025-11-25**; automatic discovery was **2026-07-28**.
The source fixture retained all **184 files unchanged**. Its snapshot matched
the original contents after deliberate negative probes were restored.

Tests cover full component and net pagination (97 components / 48 nets), raw
template/attribute reporting for R17, GND signal counts, matching MCP error flags,
response-size bounds, outside-root rejection, invalid handles/cursors/limits,
locks and recovery markers preserved, changed source and snapshot revisions,
unsupported format, malformed syntax, absent embedded device data rejected by
the real CLI, missing CLI readiness and session isolation. The process timeout
test uses a real Python subprocess; it is not a LibrePCB timeout integration test.

## Files in this packet

- `mcp-integration.json`: all 82 assertions, 27 tool calls and protocol records.
- `tool-schemas.json`: the five tool definitions actually returned by MCP.
- `codex-host.json`: actual installed host results and seven assertions.
- `unit-tests.txt`: full final test output.
- `dependencies.json`: exact installed versions, wheel hashes, lock hash,
  fresh-environment details and bootstrap result.
- `sdk-server-stderr.txt`, `codex-host-stderr.txt`: both empty in the final runs.
- `raw/`: 20 CLI stdout/stderr artifacts from the passing integration/host runs,
  including successful opens and the deliberate missing-device rejection.
- `artifact-map.json`: maps original portable artifact paths to checked-in logs.

Paths are normalized to `<REPO>` and text line endings may be normalized.
Runtime binaries, temporary copies, downloaded dependencies, host-generated
schemas, full installation reports and earlier exploratory runs remain under
ignored `work/`. No account credentials or model API keys are in this packet.

## Failures found and resolved

- Initial deep extraction paths exceeded Windows MAX_PATH on an embedded 3D
  model. Test paths and session/snapshot names were shortened, and generated
  copies now return `path_too_long` for excessive paths. No registry changes.
- The first editable install needed hatchling's `editables` dependency. It is now
  explicitly pinned along with hatchling and included in the tested hash lock.
- The initial SDK import probe used a nonexistent transport module. Installed
  v2 source and official docs established the correct imports before implementation.
- A Codex test override incorrectly quoted a dotted-key segment and created an
  invalid transport entry. The optional harness now uses the verified CLI override
  form. An early run also inherited an unrelated Cloudflare plugin that requested
  authentication; final process-local feature flags disable plugins/apps, and
  the passing host run has empty stderr. No authentication was added or changed.
- Dependency report decoding initially used the Windows default encoding;
  report readers now explicitly use UTF-8.

No known failing assertion remains. No persistent MCP server, LibrePCB process
or host-test process is needed after these runs.

## Limits of the evidence

The Codex test uses an ephemeral app-server thread and direct MCP calls. It is
not a UI click-through, a model-generated board review, or a Claude connection.
It submits no model turn. Personal client configurations are unchanged.

Day 2 verifies inspection only. Model-facing checks/previews/exports, deliberately
introduced wiring/DRC faults, GUI save/reopen, edits/rollback, owner electrical
review and fresh-machine installation remain pending. Day 1's direct CLI
check/export evidence is preserved separately and was not rerun during Day 2.
