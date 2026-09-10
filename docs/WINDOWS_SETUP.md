# Windows development quickstart

This sets up and verifies the Day 1 foundation. It does not start an MCP server yet.

## Existing workspace

From PowerShell in this repository:

```powershell
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v
& '.\.venv\Scripts\python.exe' scripts/verify_baseline.py
```

Expected: six adapter tests pass; the baseline reports `passed: true` with thirteen checks. The baseline uses the real LibrePCB executable, not a stub. It creates a fresh folder under `work/runs/` containing the report, raw logs, unchanged baseline copy, negative-test copies and output files.

Open `work/runs/<new-run>/preview/schematic1.png` and `schematic2.png` to inspect the result. Manufacturing outputs are under `exports/gerber/`. Their generation is a compatibility test, not approval to manufacture a board.

## Set up prerequisites

Use a real Python 3.12+ interpreter; this session tested 3.12.14. The bootstrap script verifies the pinned LibrePCB archive hash, extracts the portable runtime into `work/`, verifies its CLI signature, and creates a local venv. It downloads approximately 85 MB if the archive is missing. It does not modify global settings.

On this machine the known interpreter is:

```powershell
& '.\scripts\bootstrap.ps1' -PythonExe 'C:\Users\vboxuser\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
```

On another machine pass the absolute path to its Python executable. The default `python` only works when it resolves to an actual interpreter. If the coding sandbox requests network/Git permission, use its normal approval flow.

No `pip install` is needed at Day 1. SDK installation and package metadata are Day 2 work. Do not assume Python dependencies from Codex's base environment are installed in this isolated venv.

## Reproducibility notes

- Versions, URLs, observed SHA256 hashes and fixture revision live in `toolchain.json`.
- The CC0 fixture is committed as an unchanged `.lppz` archive. The baseline verifies its hash before unpacking anything. It never edits the fixture archive.
- Each run uses a unique directory. No existing output is replaced.
- The baseline intentionally writes two negative copies: one without ERC approvals, one with malformed circuit syntax. Do not open these as the positive demo.
- Downloaded executables, venv and generated files are ignored by Git. When transferring to Claude on another computer, send the repository and let the recipient recreate prerequisites. A local client on this same PC can use the existing files immediately.
- Raw evidence paths use `<REPO>` as a portable placeholder for this repository's absolute path.
- The bootstrap script was exercised with prerequisites already present. Fresh-machine installation and an actual user-followed quickstart remain Day 6 acceptance work.
