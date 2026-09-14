# Recorded development environment

Verified locally through 2026-09-14. Paths describe this machine; use explicit arguments on another machine.

| Item | Observed value |
| --- | --- |
| OS | Windows 11 x64, NT 10.0.26200.0 |
| Shell / culture | PowerShell; en-US |
| Git | 2.45.1.windows.1 |
| Python | 3.12.14 |
| Local venv pip | 25.0.1 |
| LibrePCB CLI | 2.1.1 |
| LibrePCB format | 2 (stable) |
| LibrePCB revision | 06465bf (2026-06-12) |
| Qt | 6.10.1, compiled against 6.10.1 |
| OpenCascade | 7.9.1 |
| MCP SDK | 2.2.0; all 36 runtime/build dependencies pinned with wheel hashes |
| Package / build backend | 0.1.0.dev6 / hatchling 1.32.0, editables 0.6 |
| MCP protocols tested with SDK | 2025-11-25 (legacy), 2026-07-28 (automatic) |
| Installed host tested | codex-cli 0.153.4, direct app-server MCP calls |
| GitHub CLI | 2.100.0, verified official Windows portable download; development publication only |
| GUI / Claude | Actual LibrePCB GUI save/reopen tested in isolation; Claude connection untested |

## Exact paths

Repository:
`C:\Users\vboxuser\Documents\Codex\2026-09-10\help-me-write-a-good-prompt\outputs\librepcb-mcp-server`

Base Python (discovered through Codex desktop's workspace runtime):
`C:\Users\vboxuser\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`

Project interpreter: `<repository>\.venv\Scripts\python.exe`.

Portable CLI: `<repository>\work\tools\librepcb-2.1.1\bin\librepcb-cli.exe`.

Portable GUI executable is in the same binary directory. Day 4 opened/saved/reopened a disposable candidate in the actual GUI, with isolated `LIBREPCB_WORKSPACE=work/d4g/ws` and `LIBREPCB_CONFIG_DIR=work/d4g/config` (absolute paths in the child environment). Normal workspace settings were not changed.

No global Python, PATH, registry, Git config, Codex MCP config or Claude config
changes were made. The venv depends on its base interpreter; if the desktop
runtime is removed, recreate it using Python 3.12 x64 and the dependency lock.

Fresh verification interpreter: `<repository>\work\v2\Scripts\python.exe`.
Its 36 hash-locked dependencies were installed in Day 2. Day 3 replaced the
editable install with a wheel. Day 4 installed the noneditable `0.1.0.dev4` wheel, verified site-packages
and resource loading, and passed `pip check`. The full Day 4 candidate acceptance
is recorded in the Day 4 evidence packet. Its wheel is under `work/day4-wheel/`.
Day 5 replaced that wheel with noneditable `0.1.0.dev5`, passed all four SDK
acceptance/regression harnesses and the Codex host, and passed `pip check` in both
environments. The tested wheel and hash are recorded in the Day 5 packet.
This environment remains dev5. Day 6 created a new checkout and environment at
`C:/Users/vboxuser/AppData/Local/Temp/lp-d6-c6010a/LibrePCB trial`; it downloaded and
verified the portable runtime, installed locked dependencies, passed default and
experimental walkthroughs, repeat setup and 57 unit/adapter tests, then installed
the noneditable dev6 wheel and passed its 26-check/12-call walkthrough. Exact
commands, hashes and module locations are in `evidence/2026-09-14-day6/`.
Main `.venv` is editable dev6. These are isolated environments on the same Windows
host; existing base Python, certificate store and pip cache remain available.
Windows PowerShell 5.1 setup is verified with process-only RemoteSigned and the
edition's own built-in modules; registry policy and global module paths unchanged.

Tested Codex executable:
`C:\Users\vboxuser\AppData\Local\OpenAI\Codex\bin\fd4c151a749f3ab4\codex.exe`.
The deterministic harness used its generated app-server JSON schemas, an
ephemeral thread and direct MCP calls. No model turn was submitted. The final
test disabled other plugins/apps only in its child process and had empty stderr.
Generated host schemas are ignored under `work/research/day2/codex-schema/`.

Ready sample/config snippets: `<repository>\work\demo-e8a9b4\`.
See `docs/WINDOWS_SETUP.md`; snippets have not been installed in a client.

## Downloads and integrity

The official stable page linked the portable ZIP in `toolchain.json`. It was downloaded over HTTPS to `work/downloads/`, hashed locally, then extracted under `work/tools/`.

- ZIP: 85,142,354 bytes, SHA256 `5fed82a57ede5e807bca4a737108389c64fbd323d29b967dbb2eafa63b6cb3ae`.
- CLI Authenticode status: **Valid**, “Signature verified.”
- Signer: Cloudyne Systems (Scheibling Consulting AB), Sweden.

The ZIP hash is the observed download hash, not an independently obtained upstream checksum. The executable signature was verified separately. No runtime binaries are committed or repackaged.

## Git and sandbox behavior

`.git` was created by the sandbox account `W11/CodexSandboxOffline`. Git run as the normal user initially reported dubious ownership. Local commits worked with a per-command setting scoped to this folder:

```powershell
git -c safe.directory=C:/Users/vboxuser/Documents/Codex/2026-09-10/help-me-write-a-good-prompt/outputs/librepcb-mcp-server status --short
```

Use the same scoped option for `add`/`commit` when required. The coding environment may require approval for Git writes or downloads; do not bypass that with another tool or a wildcard trust setting. The initial checkpoint is `0941493`. Remote `origin` is the owner-requested private `https://github.com/sulaimwn/LibrePCB-MCP-Server.git`, branch `master`. GitHub CLI is `work/tools/gh-2.100.0/portable/bin/gh.exe`; its existing authenticated account created the repo. Pushes use a per-command Git credential helper invoking that CLI, without global config changes. Never put credentials in project files.

## Windows CLI findings

- Do not force `QT_QPA_PLATFORM=offscreen`. It hung this build before even printing `--version`, under both ordinary and hidden process launch. The adapter removes that inherited setting on Windows.
- `CREATE_NO_WINDOW` alone works; no helper GUI window needs to be opened.
- `LC_ALL=C` is set by the adapter, but tests were only run with the host culture en-US. The Day 3 parser rejects unknown/localized output conservatively; other locales are unverified.
- Real rule findings print in **stderr** while counts are in **stdout**. Preserve both.
- Raw diagnostics go to unique files capped at 2,000,000 bytes per stream; reaching the cap stops the child with `output_limit`. Excerpts remain 4,000 bytes per stream.
- Keep data paths short. Deep extraction initially hit Windows MAX_PATH; the
  server now checks generated paths and uses compact session/snapshot folder names.
