# Day 1 implementation evidence

Session: ChatGPT/Codex, 2026-09-10, Windows/PowerShell. Owner authorized starting implementation and requested substantial context for Claude handoff.

## Passing real LibrePCB baseline

Run ID: `baseline-20260910T221549Z-4895e4b1`.

Command from repository root:

```powershell
& '.\.venv\Scripts\python.exe' scripts/verify_baseline.py
```

**Result: PASS, 13 assertions, 8 actual CLI invocations.** Read `baseline.json` for exact argument arrays, process outcomes/times, diagnostics, source fingerprint and generated artifact hashes. `<REPO>` means the absolute repository root. `source-manifest.json` contains the SHA256 of every extracted project file.

| Probe | Actual result |
| --- | --- |
| Version | CLI 2.1.1, stable format 2, revision 06465bf |
| Help | Real flags captured in `open_project_help.stdout.txt` |
| Strict load | Exit 0, canonical project |
| ERC | 2 approved, 0 unapproved |
| DRC, board default | 16 approved, 0 unapproved |
| PDF + manufacturing | Exit 0; schematic PDF, 9 Gerbers, 2 drill files |
| PNG graphics job | Exit 0; two 1760×1245 pages |
| Preservation | All 184 extracted files and original archive unchanged |
| ERC negative copy | Remove approval records only; exit 1 and two open-wire warnings |
| Malformed negative copy | Truncate circuit S-expression; exit 1 and explicit parse error |

The per-command `<name>.stdout.txt` / `<name>.stderr.txt` files in this folder are normalized copies of raw CLI output. Empty stderr files are retained to show which commands produced no stderr. The original raw byte streams and generated output are under the ignored run folder.

Source-manifest digest: `e3eff77e30d22e342471f2b3122c8f28bdc5d0dfef7ed596d877fb2b3cf151b4`.

The ERC negative test re-exposes **existing** findings. It does not prove that a newly introduced wiring error or physical DRC fault is detected. Those examples are still Day 3 work. No generic diagnostic parser exists yet; the harness's count assertions are fixture-specific.

## Adapter tests

```powershell
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v
```

Final run: **6 tests passed**, 1.345 seconds. These start real Python subprocesses to test literal argument passing (including spaces and shell-looking text), nonzero exits, bounded excerpts/raw-log retention, noncolliding artifacts, timeout/termination, missing executables, launch failures and invalid timeouts. They are process-adapter tests, not substitutes for LibrePCB integration.

`scripts/bootstrap.ps1` also passed against the already-installed prerequisites. The fresh-install branch remains untested as a scripted end-to-end flow. Initial venv creation, official ZIP download, extraction, signature verification and version tests were performed directly and succeeded.

Both schematic sheets were inspected with the image viewer. The outputs show the Main and Ethernet schematics with symbols, labels, wiring and page frames. No claim is made about circuit suitability or physical board correctness. No interactive GUI review or PDF rendering was performed.

## Failures and discoveries retained for the next client

1. **Network sandbox:** PowerShell download attempts initially failed with forbidden socket access. Reissued through normal permission escalation and succeeded.
2. **Git sandbox/ownership:** `git init` succeeded; writing the index required escalation. Elevated Git then rejected sandbox-owned `.git`. Per-command `safe.directory` for this exact folder fixed it. No global config or remote was added.
3. **Deprecated export:** exploratory `--export-schematics .../schematic.png` produced two PNGs but exited **2**, with a deprecation warning. Do not use this as the product preview path. The `--jobs ... --run-job "Schematic PNG"` command is verified and returns 0.
4. **Forced Qt offscreen hang:** first automated run (`baseline-20260910T221414Z-f14cdad3`) hung on `--version` and was killed after 60 seconds. A separate three-case probe confirmed ordinary launch and `CREATE_NO_WINDOW` both work, while `QT_QPA_PLATFORM=offscreen` alone times out after 8 seconds. No output was emitted before the timeout. The adapter now removes that setting on Windows. The failed run's `version-failure.json` remains in `work/runs/`.
5. **Warnings on stderr:** negative ERC findings print on stderr, while counts appear on stdout. Malformed project loading also returns 1. Preserve and inspect both streams; do not equate every nonzero exit with a crash or a rule violation.
6. A Python docstring initially emitted an invalid-escape warning; corrected to slash paths before final validation.

## Actual commands and tool sources

The automated exact commands are in `baseline.json`. Initial exploratory calls used the same pinned binary with `--version`, `open-project --help`, `--strict`, `--erc --drc`, the existing PDF/Gerber jobs and the deprecated-export probe described above. No `--save` was run on the design.

Official portable download: https://download.librepcb.org/releases/2.1.1/librepcb-2.1.1-windows-x86_64.zip

Fixture source/license notes: `tests/fixtures/README.md` and `toolchain.json`.

## Handoff

No project-owned process remains running. Day 1 is complete. Follow STATUS.md into Day 2: official MCP SDK selection/pin, STDIO handshake, allowlisted saved-project handles, and structured format-2 parsing. This session did not implement or claim a working MCP server.
