# Recorded development environment

Verified locally on 2026-09-10. Paths describe this machine; use explicit arguments on another machine.

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
| Third-party Python libraries | None installed in project environment |
| MCP SDK / host integration | Not yet selected/tested |

## Exact paths

Repository:
`C:\Users\vboxuser\Documents\Codex\2026-09-10\help-me-write-a-good-prompt\outputs\librepcb-mcp-server`

Base Python (discovered through Codex desktop's workspace runtime):
`C:\Users\vboxuser\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`

Project interpreter: `<repository>\.venv\Scripts\python.exe`.

Portable CLI: `<repository>\work\tools\librepcb-2.1.1\bin\librepcb-cli.exe`.

Portable GUI executable is in the same binary directory. The interactive application has not been launched for this project. Do not change the user's workspace settings to test it.

No global Python, PATH, registry, Git config, Codex MCP config or Claude config changes were made. The venv depends on its base interpreter; if the desktop runtime is removed, recreate the venv using a separately installed Python 3.12+.

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

Use the same scoped option for `add`/`commit` when required. The coding environment may require approval for Git writes or downloads; do not bypass that with another tool or a wildcard trust setting. The initial checkpoint is `0941493`. No Git remote exists.

## Windows CLI findings

- Do not force `QT_QPA_PLATFORM=offscreen`. It hung this build before even printing `--version`, under both ordinary and hidden process launch. The adapter removes that inherited setting on Windows.
- `CREATE_NO_WINDOW` alone works; no helper GUI window needs to be opened.
- `LC_ALL=C` is set by the adapter, but tests were only run with the host culture en-US. Do not assume localized output is fully handled by the upcoming domain parser.
- Real rule findings print in **stderr** while counts are in **stdout**. Preserve both.
- Raw diagnostics go to unique files. Only 4,000 bytes per stream are included in the returned adapter record.
