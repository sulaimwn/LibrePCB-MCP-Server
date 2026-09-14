# Windows development quickstart

Package `0.1.0rc1` supports saved-project inspection, checks, native PNG/PDF/Gerber exports
and opt-in typed-resistance candidates through a local STDIO MCP server. Tested:
Windows x64, Python 3.12.14, LibrePCB 2.1.1, MCP SDK 2.2.0.

For a first run, follow **Set up prerequisites**, then **Prepare a sample and
client configuration** below. The longer regression commands are for development.

## Existing workspace: verify it

Run from PowerShell in this repository:

```powershell
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v
& '.\.venv\Scripts\python.exe' scripts/verify_mcp.py
& '.\.venv\Scripts\python.exe' scripts/verify_day3.py
& '.\.venv\Scripts\python.exe' scripts/verify_day4.py
& '.\.venv\Scripts\python.exe' scripts/verify_day5.py
```

Expected: 57 tests pass, inspection reports `passed: true` with 82 checks / 27
MCP calls, Day 3 reports 73 checks / 20 calls, and Day 4 reports 103 checks / 30 calls. Day 5 adds 38 reliability checks, seven completed MCP calls, two cancelled requests and 26 observed direct CLI invocations. All four harnesses use SDK clients,
the real server and real LibrePCB; they do not call a model. Unique copies and
logs go under `work/d2-<id>/`, `work/d3-<id>/`, `work/d4-<id>/` and `work/d5-<id>/`, with exact `report.json` results.
Server processes stop at completion. Allow several minutes per larger harness.

For the optional installed Codex host test:

```powershell
& '.\.venv\Scripts\python.exe' scripts/verify_codex_host.py --codex 'C:\Users\vboxuser\AppData\Local\OpenAI\Codex\bin\fd4c151a749f3ab4\codex.exe'
```

Expected: 12 checks / 10 calls pass, including all eight tools, native image
bytes, checks, PDF and manufacturing exports. The executable path is specific
to this machine. The ephemeral host thread uses direct tools, without a model
turn or persistent config edits. Add `--experimental-edits` to that harness for 15 checks / 13 calls, including
the ninth tool and edited candidate image. Host image delivery passed. Actual
LibrePCB GUI save/reopen was tested separately; Codex UI and Claude remain untested.

## Set up prerequisites

Use a real **Python 3.12 x64** interpreter. The bootstrap verifies the pinned
LibrePCB ZIP hash and CLI signature, extracts the portable runtime, creates
`.venv`, installs hash-pinned dependencies and installs the local editable package.
It downloads about 85 MB of LibrePCB plus Python dependencies when absent.

```powershell
powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File '.\scripts\bootstrap.ps1' -PythonExe 'C:\Users\vboxuser\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
```

On another machine, pass its Python 3.12 x64 executable. A WindowsApps alias is
not sufficient. The lock is specific to this Python/Windows combination.
The command applies `RemoteSigned` only to this new setup process; it does not
change registry-backed policy. Windows PowerShell's default `Restricted` policy
blocked the original quickstart on the clean-checkout trial. Managed group policy
still takes precedence. See [Microsoft's process option](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_powershell_exe?view=powershell-5.1#-executionpolicy-executionpolicy).
The equivalent Python installation steps, after creating a venv, are:

```powershell
& '.\.venv\Scripts\python.exe' -m pip install --require-hashes -r requirements.lock
& '.\.venv\Scripts\python.exe' -m pip install --no-deps --no-build-isolation -e .
& '.\.venv\Scripts\python.exe' -m pip check
```

Day 6 followed this command from a fresh GitHub checkout with no local venv or
LibrePCB runtime. The download, verification and installation passed on the same
Windows machine. See [Day 6](DAY6.md) for the recorded trial and its limits.
An owner-followed installation on another Windows machine remains unverified.
Failed downloads are retained as unique `.partial` files and are not used as the
cached ZIP. A corrupt cached ZIP is refused and preserved for inspection.

## Prepare a sample and client configuration

```powershell
& '.\.venv\Scripts\python.exe' scripts/prepare_demo.py --verify
```

This creates a new `work/demo-<id>/` containing the unchanged CC0 sample in `p/`,
`codex-config.toml`, `claude-desktop-config.json`, and `sample-prompt.txt`. The
`--verify` option exercises the generated configuration through actual MCP/CLI
calls and writes a `review-<id>/` with images, PDF and a result report. Expect
**21 checks / 10 calls** by default. See [the sample walkthrough](OWNER_TRIAL.md).
The snippets contain absolute paths for the interpreter, CLI, allowed sample
root and separate snapshot/log data directory. The script does not install
them into a client or change existing settings. A ready sample from this
session is `work/demo-e8a9b4/`, generated with `--experimental-edits --verify`. To generate
that variant yourself, add `--experimental-edits` to `prepare_demo.py`; it enables
the ninth tool and raises the generated Codex tool timeout to 300 seconds. The
default command still generates the eight-tool configuration. The experimental
sample check expects **26 checks / 12 calls**. Generating/checking a configuration
does not install it into your live conversation; owner review remains separate.

For Codex, merge the generated `mcp_servers.librepcb` table into the appropriate
trusted project or user config, preserving existing tables. For Claude Desktop,
merge only its `librepcb` entry into the existing `mcpServers` object using the
client's configuration editor, then restart that client. Claude Desktop's
snippet is documentation-based and has not been tested here. Claude Code is a
different client; use its own local MCP registration with the generated command
and argument list. Sources: [Codex configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
and [official SDK host guide](https://py.sdk.modelcontextprotocol.io/get-started/real-host/).

The host launches the server on demand; no port, hosted service or model API key
is required. Start with `get_status`, then `open_project` on the absolute `.lpp`
path, then use the returned `project_id` for summary/components/nets. Use returned
cursors unchanged. Then call `run_checks`, `export_preview`, and supported
`run_output_job` jobs. Default Codex config allows 120 seconds per tool (300 with experimental edits) for
combined CLI operations; longer custom CLI timeouts need a longer host timeout.
The sample prompt is included beside the configuration.

To inspect a personal project later, configure its containing directory as a
`--project-root`, close it in LibrePCB, and supply its extracted `.lpp` path.
Keep `--data-root` separate and reasonably short. The server rejects locks,
recovery data, linked paths, unsupported formats and stale revisions. See
[inspection limits](DAY2.md), [Day 3 exports](DAY3.md) and [Day 4 candidate
lifecycle/rollback](DAY4.md), and [Day 5 cancellation/deadlines/recovery](DAY5.md). Only separate candidates are edited. Use decimal
strings in the existing resistance unit, and the source's current revision.

## Direct CLI baseline and artifacts

```powershell
& '.\.venv\Scripts\python.exe' scripts/verify_baseline.py
```

The Day 1 baseline has 13 assertions over eight real CLI invocations. Fresh
copies, PNG previews and manufacturing outputs go under `work/runs/`. This is
the historical direct-CLI baseline. The Day 3 harness above verifies these
capabilities through MCP; the direct baseline alone does not prove client integration.

Version pins and hashes live in `toolchain.json` and `requirements.lock`.
The fixture is committed unchanged; every harness verifies its hash before
extraction. `work/` and `.venv/` are ignored by Git and should be recreated if the
repository moves machines. Retained logs and snapshots are not automatically
cleaned up. Do not delete directories used by an active host. Evidence paths
use `<REPO>` as a portable placeholder for the absolute repository path.
