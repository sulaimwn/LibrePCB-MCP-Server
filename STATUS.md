# Current project status

Updated: 2026-09-10, approximately 18:25 America/Toronto. Active coding client: ChatGPT/Codex. Ready for a single-writer handoff.

## Current milestone

**Day 1 complete — real LibrePCB CLI baseline verified. Day 2 is next.**

This is a working foundation, not a release or connected MCP server. No model-facing tools, project parser, value-edit feature, packaging or live GUI integration exist yet.

## Completed this session

- Read all original Markdown instructions and the owner's entire pasted conversation. Saved relevant owner context in `docs/OWNER_CONTEXT.md`; preserved `.claude` local settings, now ignored by Git.
- Initialized local Git and made the initial planning/context checkpoint `0941493`. No remote, upload or publication. Final Day 1 checkpoint contains the implementation and evidence; inspect `git log -2 --oneline` for its hash.
- Created `.venv` using the available desktop-bundled Python **3.12.14**. The WindowsApps alias is not a usable interpreter. No third-party Python dependencies installed; MCP SDK is not selected.
- Downloaded the official portable Windows **LibrePCB 2.1.1**, recorded ZIP SHA256, verified the CLI's Windows signature, and ran its real version/help commands. File format 2, revision 06465bf, Qt 6.10.1, OCCT 7.9.1.
- Vendored the unmodified **CC0 D0 reader** fixture archive from a pinned official repository revision, with source/license notes and a copied license.
- Implemented an internal process adapter with argument arrays, finite timeout, hidden console, unique raw logs and bounded excerpts. It does not expose a shell tool or enforce a model-facing project-root policy; that policy belongs in the upcoming domain layer.
- Implemented the repeatable Day 1 integration harness, a trusted PNG output job and a local bootstrap script.

## Files added or changed

- `src/librepcb_mcp/adapters/cli.py`, package markers: process adapter, not MCP transport.
- `scripts/verify_baseline.py`, `scripts/bootstrap.ps1`: reproducible CLI baseline and Windows prerequisites.
- `resources/preview-jobs.lp`, `toolchain.json`: tested output-job configuration and version/hash pins.
- `tests/test_cli_runner.py`, `tests/fixtures/`: six process tests and the redistributable sample.
- `evidence/2026-09-10-day1/`: checked-in report, all eight command stdout/stderr pairs, source manifest and session notes.
- `docs/OWNER_CONTEXT.md`, `docs/ENVIRONMENT.md`, `docs/WINDOWS_SETUP.md`, `docs/DECISIONS.md`: durable context for the next client.
- Updated `.gitignore`, `.gitattributes`, README, PLAN, SPEC, RESEARCH, HANDOFF, CLAUDE and this status file.
- Ignored `work/`: downloaded runtime, initial exploratory files, disposable test copies, exports and raw logs. `.venv/` is also ignored.

## Checks actually run

1. `.venv/Scripts/python.exe scripts/verify_baseline.py` — **PASS, 13 assertions across 8 real CLI invocations** on the final run.
   - Strict open passed. ERC: 2 approved / 0 unapproved. DRC: 16 approved / 0 unapproved.
   - Exported two 1760×1245 PNG schematic pages, one schematic PDF, nine Gerbers and two Excellon drill files.
   - All 184 extracted project files and the source archive stayed unchanged.
   - Exposing existing ERC approvals returned 1 with two warnings; malformed syntax also returned 1 with a parse error. This proves exit code alone cannot distinguish them.
2. `.venv/Scripts/python.exe -m unittest discover -s tests -v` — **6 tests passed** after the adapter fix. These use real Python subprocesses; they are adapter tests, not LibrePCB integration tests.
3. `scripts/bootstrap.ps1` with the documented Python path — passed on already-present prerequisites. The script's fresh-machine path has not been tested; initial download/extraction/venv creation was performed with equivalent explicit commands.
4. `git diff --check` — passed during review; staged whitespace check performed at the final checkpoint.
5. Visually inspected both schematic sheets using the image viewer. No interactive LibrePCB GUI opening, save/reopen, owner electrical review, or PDF page rendering was performed.

Passing run: `work/runs/baseline-20260910T221549Z-4895e4b1/`.
Durable report: `evidence/2026-09-10-day1/baseline.json`.

## Failures encountered and resolved

- Sandbox blocked network and `.git/index.lock`: handled via normal escalation. Git additionally saw sandbox-vs-owner ownership; used per-command `safe.directory` scoped to this exact repository, without global configuration changes.
- Forcing Qt offscreen mode hung CLI `--version`; the timeout terminated it. The runner now uses native Windows Qt behavior and hides the console. Failed-run details: `work/runs/baseline-20260910T221414Z-f14cdad3/version-failure.json` and evidence README.
- Deprecated `--export-schematics` generated PNGs but exited 2. Switched to a supported graphics output job, which exited 0.
- A docstring escape warning was corrected. No known failing assertion remains in the current baseline/tests.

## Running processes / incomplete operations

No project-owned server, LibrePCB process, download or test is left running at handoff. Unrelated pre-existing Claude processes were not touched. No automation has been scheduled.

## Next task — start here

**Day 2: build and test the smallest local MCP connection plus saved-project inspection.**

1. Read `docs/ENVIRONMENT.md`, `docs/DECISIONS.md` and the real logs; reuse the existing prerequisites. Inspect Git and honor one writer at a time.
2. Verify the current official MCP Python SDK interfaces from its docs/source, choose an exact stable version, create `pyproject.toml` and a pinned/locked dependency workflow, and install into this `.venv`.
3. Add transport separately from domain operations. First tools: `get_status` and allowlisted `open_project`; use opaque handles, file-format rejection, saved-state labeling, safe paths and revision fingerprints. Address `.lock`, `.autosave` and `.backup` explicitly.
4. Implement a real S-expression parser and documented format-2 subset for metadata, component references/raw values, attributes and nets. Do not treat `{{RESISTANCE}}` as an already-resolved resistor value. Preserve identifiers and reject unsupported shapes.
5. Run an actual STDIO MCP handshake and calls using an SDK client, then the selected installed host if available. Document exactly which client was tested; an SDK client is not a Codex/Claude Desktop UI test.
6. Keep rule violations separate from CLI failure. The model-facing checks/preview layer is Day 3; its allowlists, log limits and output-job path validation must be in place before tools are exposed.

Do not add write tools until the read/check/export **MCP workflow** is verified. Day 1 CLI success alone does not finish Day 3. The value-edit gate still requires a candidate copy, semantic invariants, CLI/GUI reopen checks, checks comparison and rollback evidence.

## Nonblocking owner decisions

- Public software license (required before distribution; CC0 fixture license is separate).
- Exact Claude client/local access and daily available time.
- Owner's preferred personal design for a later trial.

These do not block Day 2 development. No subscription credentials or model API keys are needed for the server itself.
