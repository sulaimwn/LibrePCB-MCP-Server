# Current project status

**Day 4 is now in progress at the owner's request.** Codex remains the active
writer; no Claude handoff is planned. Regular GitHub checkpoints are authorized.
The completed Day 3 record below remains as the baseline until Day 4 validation
is recorded. First task: verify typed resistor semantics and isolated GUI/save
lifecycle, then implement the smallest validated candidate-edit operation.

Day 4 proof checkpoint: `adapters/edits.py` implements a typed scalar patch and
exact full-file invariants; **seven new unit tests passed**. The real CLI
strict/save/strict probe passed at `work/d4p-89d75/`. A disposable candidate
opened in the actual GUI, visibly showed R17 at 2.2 kΩ, saved, and reopened in
a new GUI process with the value retained. An independently GUI-saved unmodified
control matches all 188 candidate files except the intended resistance scalar.
The four added files are editor preferences, including board-layer visibility.
All 184 original source files remain untouched. Evidence/screenshots are in
`evidence/2026-09-11-day4/`; details in `docs/DAY4.md`. No GUI remains running.
MCP edit registration, full checks/export comparison and rollback are next;
Day 4 is not complete at this checkpoint. Codex continues after this push.

Updated: September 11, 2026, America/Toronto. Active coding client: ChatGPT/Codex.
Owner chose Codex to complete Day 3 and explicitly requested GitHub publication
as **LibrePCB-MCP-Server**, with a WIP README. This supersedes the earlier Claude
handoff plan; the handoff files remain available for future continuity.

## Current milestone

**Days 1–3 complete. Next: Day 4's one-value edit experiment.**

Package **0.1.0.dev3** implements eight STDIO MCP tools on Windows x64 / Python
3.12.14 / MCP SDK 2.2.0 / LibrePCB 2.1.1 (stable format 2): `get_status`,
`open_project`, `get_project_summary`, `list_components`, `list_nets`,
`run_checks`, `export_preview`, and `run_output_job`.

Real SDK clients and the installed Codex host passed inspection, checks, native
PNG delivery, PDF and Gerber/Excellon exports. No design-edit tool exists and no
release is claimed. Current operations preserve the source design.

GitHub: [sulaimwn/LibrePCB-MCP-Server](https://github.com/sulaimwn/LibrePCB-MCP-Server),
**private**, branch `master`, remote `origin`. Private was the stated default
because visibility was unspecified. Source, tests, docs, fixture, evidence and
existing commit history are included. Runtimes, environments, temporary work and
credentials remain ignored. This checkpoint is the completed Day 3 upload;
use `git log -1` for its commit ID.

## Completed in Day 3 / files changed

- `src/librepcb_mcp/adapters/checks.py`: conservative ERC/DRC interpretation,
  separate approved/unapproved counts, valid violation results and explicit
  indeterminate errors for unknown, incomplete or contradictory diagnostics.
- `adapters/exports.py` and packaged `resources/preview.lp`, `gerber.lp`:
  fixed server-owned PNG/PDF/manufacturing jobs, validated board selection,
  fresh output directories, control-manifest checks, artifact hashes and limits.
- `adapters/cli.py`: capped diagnostic files, simultaneous stream draining,
  finite timeout and explicit `output_limit` failure.
- `service.py`, `server.py`: three new tools, lock/revision checks around CLI
  operations, bounded structured results and native PNG `ImageContent`.
  These paths are under `src/librepcb_mcp/`.
- Package advanced to `0.1.0.dev3`; the 36 dependency pins and fixture archive
  are unchanged. Installed-wheel job resources were verified.
- `scripts/day3_fixtures.py`, `verify_day3.py`: reproducible real faults and
  full MCP checks/export/image acceptance. Inspection and Codex host harnesses
  cover all eight tools. Generated Codex config allows 120 seconds per tool.
- `tests/test_checks.py`, `test_exports.py`, `test_cli_runner.py`: ambiguous
  diagnostics, Unicode bounds, manifest/path/tampering and output flooding.
- WIP README with a real MCP image; current PLAN, SPEC, HANDOFF, CLAUDE,
  RESEARCH, setup/environment/decision notes and `docs/DAY3.md`.
- `evidence/2026-09-11-day3/`: reports, 90 CLI log files, 12 operation reports,
  schemas, unit output and build/environment hashes. Day 1/2 evidence unchanged.

## Checks actually run

| Check | Result and local run |
| --- | --- |
| Full unit/adapter suite | **33 passed** in 17.153 s; `work/day3-unit-tests.txt`, `.venv`. Includes actual Python subprocess and Windows filesystem tests; synthetic parser/export examples are unit fixtures. |
| SDK inspection regression | **82 checks / 27 calls passed**, `work/d2-33b330/`, editable Day 3 package. Both recorded protocol negotiations and saved-state/negative-project cases passed. |
| SDK checks/export/image acceptance | **73 checks / 20 calls passed**, final **installed wheel** in `work/v2`, `work/d3-a225dc/`. Earlier editable run also passed at `work/d3-cada83/`. |
| Installed Codex 0.153.4 host | **12 checks / 10 calls passed**, `work/cx-2957d9/`. All eight tools, checks, native PNG/hash, PDF, 11 manufacturing files and outside-root rejection. Final stderr empty. |
| Package/dependencies | Built Day 3 wheel, installed noneditable in existing isolated `work/v2`, verified site-packages/resource loading and ran full Day 3 acceptance there. `pip check` passed in both environments. |
| Visual inspection | Actual Codex-received Main and SDK-received Ethernet PNGs inspected, each 1754 × 1239. README uses unchanged Ethernet image. |
| Demo generation | `scripts/prepare_demo.py` created `work/demo-5d07c4/`, unchanged sample and client snippets. No persistent client config changed. |
| Final consistency review | **30 checks passed**: documentation links, report assertions, dependency/fixture hashes, exact tested-wheel source/resources, demo config parsing and Git whitespace. `evidence/2026-09-11-day3/final-review.json`. |

Fixture: **97 components, 48 nets, one board, two sheets**, 2 ERC and 16 DRC
approvals, zero unapproved findings. A new unconnected net produced one real ERC
warning; narrowing a trace to 0.01 mm produced one real DRC error. Both became
valid violation results. All 184 source files and test sources remained unchanged
during MCP operations. Tests also preserve occupied output data, reject unknown
selectors/locks, and prove an escaping project-owned output job is not run.

The Codex test uses an ephemeral app-server thread and direct MCP calls. Usable
image delivery and subsequent agent visual inspection passed. A model turn,
UI click-through, live chat installation or Claude connection is not claimed.
Day 1's direct CLI baseline was not rerun in Day 3.

## Failures resolved / remaining limits

- Initial export validation rejected LibrePCB's hidden `.librepcb-output` file.
  The adapter now validates its relative paths, exact job UUID and artifact set.
- Fixed A4 paper and static basenames bound preview dimensions and prevent
  project/variant names from determining export paths. Diagnostic summaries
  enforce encoded byte budgets; capped logs cannot imply a clean check.
- No known failing assertion remains. Coverage is one real example and two
  faults, not arbitrary designs or localized CLI output.
- Revision checks assume cooperative local access, not an atomic transaction.
  Direct-child termination is not general process-tree supervision. Export size
  limits apply after rendering, not as an OS disk quota. Cleanup is manual for
  inactive sessions; raw logs and copies otherwise remain.
- Display-template evaluation, design serialization, GUI save/reopen, edits,
  rollback, personal designs, fresh-machine installation and Claude are untested.
  Server license selection and owner trial remain open; the fixture is CC0.

## Running processes / incomplete operations

No project-owned MCP server, LibrePCB or Codex host-test process remains running.
No test/download is pending. Other desktop sessions were not stopped. No model
API call, automation, hosted deployment, maintainer contact, credential change
or persistent MCP config change was performed. The owner-requested GitHub
repository was created and receives the project checkpoints.

## Next task — Day 4, when requested

1. Read AGENTS, STATUS, PLAN, SPEC, `docs/DAY2.md`, `docs/DAY3.md`, DECISIONS,
   ENVIRONMENT and the latest evidence README; inspect Git. Reuse `.venv`, the
   portable CLI and pinned SDK. One writer at a time.
2. Prove one resistor-value change on a closed disposable candidate before
   exposing an edit tool. R17 has raw value `{{RESISTANCE}}` and a typed
   resistance attribute `1.5 kiloohm`. Verify actual value/attribute semantics
   before selecting the field to change.
3. Use parser spans or another verified structured approach; preserve unknown
   content, UUIDs/references, counts and connectivity. Check expected source
   revision and reject locks/stale inputs.
4. Reopen the candidate in LibrePCB, verify displayed value, save and reopen;
   rerun checks, previews and exports, compare approvals/findings, inspect the
   visual change, and prove rollback by discarding only the candidate. GUI
   lifecycle/save semantics have not been verified yet; do that explicitly.
5. If an edit gate fails, retain the experiment/evidence separately and keep
   the eight current tools as the usable prototype. No placement, wiring,
   routing or native-fork expansion. Update STATUS/HANDOFF before stopping.

Exact tools and commands: `docs/ENVIRONMENT.md`, `docs/WINDOWS_SETUP.md`.
Original conversation and links: `docs/OWNER_CONTEXT.md`.
