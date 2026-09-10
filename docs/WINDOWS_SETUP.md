# Windows development quickstart

Day 2 supports saved-project inspection through a local STDIO MCP server. Tested:
Windows x64, Python 3.12.14, LibrePCB 2.1.1, MCP SDK 2.2.0.

## Existing workspace: verify it

Run from PowerShell in this repository:

```powershell
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v
& '.\.venv\Scripts\python.exe' scripts/verify_mcp.py
```

Expected: 19 tests pass, then `passed: true` with 82 checks and 27 actual MCP
calls. The latter starts SDK clients, the real server and real LibrePCB CLI;
it does not call a model. Each run creates unique copies and logs under
`work/d2-<id>/`. `report.json` records exact results. All server processes stop
when the test finishes. A run can take about a minute on this machine.

For the optional installed Codex host test:

```powershell
& '.\.venv\Scripts\python.exe' scripts/verify_codex_host.py --codex 'C:\Users\vboxuser\AppData\Local\OpenAI\Codex\bin\fd4c151a749f3ab4\codex.exe'
```

Expected: seven checks pass. The executable path is this machine's current
installation. The harness uses an ephemeral host thread and direct tool calls,
without a model turn or persistent client configuration edits. This confirms
Codex host compatibility, not graphical UI rendering or a Claude connection.

## Set up prerequisites

Use a real **Python 3.12 x64** interpreter. The bootstrap verifies the pinned
LibrePCB ZIP hash and CLI signature, extracts the portable runtime, creates
`.venv`, installs hash-pinned dependencies and installs the local editable package.
It downloads about 85 MB of LibrePCB plus Python dependencies when absent.

```powershell
& '.\scripts\bootstrap.ps1' -PythonExe 'C:\Users\vboxuser\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
```

On another machine, pass its Python 3.12 x64 executable. A WindowsApps alias is
not sufficient. The lock is specific to this Python/Windows combination.
The equivalent Python installation steps, after creating a venv, are:

```powershell
& '.\.venv\Scripts\python.exe' -m pip install --require-hashes -r requirements.lock
& '.\.venv\Scripts\python.exe' -m pip install --no-deps --no-build-isolation -e .
& '.\.venv\Scripts\python.exe' -m pip check
```

The updated bootstrap passed with local prerequisites present. The locked
dependencies and package also installed into a newly created `work/v2` venv,
which passed the final unit and SDK integration tests. Fresh-machine installation
and an owner-followed trial remain Day 6 work.

## Prepare a sample and client configuration

```powershell
& '.\.venv\Scripts\python.exe' scripts/prepare_demo.py
```

This creates a new `work/demo-<id>/` containing the unchanged CC0 sample in `p/`,
`codex-config.toml`, `claude-desktop-config.json`, and `sample-prompt.txt`.
The snippets contain absolute paths for the interpreter, CLI, allowed sample
root and separate snapshot/log data directory. The script does not install
them into a client or change existing settings. A ready sample from this
session is `work/demo-bf2ee7/`.

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
cursors unchanged. The sample prompt is included beside the configuration.

To inspect a personal project later, configure its containing directory as a
`--project-root`, close it in LibrePCB, and supply its extracted `.lpp` path.
Keep `--data-root` separate and reasonably short. The server rejects locks,
recovery data, linked paths, unsupported formats and stale revisions. See
[Day 2 limits and error behavior](DAY2.md).

## Direct CLI baseline and artifacts

```powershell
& '.\.venv\Scripts\python.exe' scripts/verify_baseline.py
```

The Day 1 baseline has 13 assertions over eight real CLI invocations. Fresh
copies, PNG previews and manufacturing outputs go under `work/runs/`. This is
separate from the current MCP tool set. Exports/check tools will arrive in Day 3.

Version pins and hashes live in `toolchain.json` and `requirements.lock`.
The fixture is committed unchanged; every harness verifies its hash before
extraction. `work/` and `.venv/` are ignored by Git and should be recreated if the
repository moves machines. Retained logs and snapshots are not automatically
cleaned up. Do not delete directories used by an active host. Evidence paths
use `<REPO>` as a portable placeholder for the absolute repository path.
