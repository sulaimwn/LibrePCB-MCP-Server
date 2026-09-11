# Current project status

Updated: 2026-09-10, America/Toronto. Active coding client: ChatGPT/Codex.
Codex is continuing Day 3 at the owner's request. The Day 2 record below is retained
until the next checkpoint. GitHub upload is now authorized as `LibrePCB-MCP-Server`,
with a clearly marked work-in-progress README; visibility is being confirmed.

## Current milestone

**Days 1 and 2 complete. Day 3 in progress — MCP checks and previews.**

The local inspection prototype is package `0.1.0.dev2`. Five MCP tools work:
`get_status`, `open_project`, `get_project_summary`, `list_components`, `list_nets`.
SDK clients and the installed Codex host made actual tool calls against real
LibrePCB 2.1.1. Check/export/edit tools are not registered. No release is claimed.

## Completed in Day 2

- Verified official MCP Python SDK **2.2.0** docs and installed APIs. Pinned all
  36 runtime/build dependencies and wheel hashes for Windows x64 / Python 3.12.
  Added package metadata and installed the editable package in `.venv`.
- Built separate STDIO transport, domain service, bounded S-expression parser,
  saved-file adapter and a documented format-2 inspection projection.
- Added allowlisted local project roots, isolated byte-preserving copies,
  session-scoped handles, revision hashes and size-aware pagination.
- Reject locks/recovery, outside-root paths, traversal, links/junctions/reparse
  points, hardlinks, malformed/unsupported projects and stale source/copy revisions.
  Validate copies with the real CLI before exposing project data.
- Read the fixture's **97 components, 48 nets, one board and two schematic sheets**.
  R17's `{{RESISTANCE}}` is correctly reported as a raw template with a separate
  `1.5 kiloohm` typed attribute. It is not treated as a resolved display string.
- Prepared repeatable SDK and Codex host acceptance harnesses. The Codex harness
  uses an ephemeral app-server thread and direct MCP calls, without a model turn.
- Installed hash-locked dependencies and the editable package in a fresh
  `work/v2` environment. Ran the final SDK and unit suites there.
- Updated bootstrap, setup instructions, architecture/decision notes and this
  handoff. Generated a ready sample and Codex/Claude Desktop config snippets in
  `work/demo-bf2ee7/`. No persistent client config was edited.

## Files added or changed

- `pyproject.toml`, `requirements.lock`, `toolchain.json`: package and exact pins.
- `src/librepcb_mcp/server.py`, `service.py`, `errors.py`, `__init__.py`: five-tool
  transport, saved-design policies, error contract and version.
- `src/librepcb_mcp/adapters/sexpr.py`, `files.py`, `project.py`: parser, path/copy
  boundaries and structured inspection. Existing CLI adapter behavior is unchanged.
- `tests/test_projects.py`: 13 parser/file/real-fixture tests; six Day 1 process
  tests remain. `scripts/verify_mcp.py` and `verify_codex_host.py`: real integrations.
- `scripts/bootstrap.ps1`, `scripts/prepare_demo.py`: installation and demo setup.
- `docs/DAY2.md`: implementation contract, subset, limits, SDK API and sources.
- `evidence/2026-09-10-day2/`: reports, actual tool schemas, unit output, dependency
  record, 20 CLI log files and artifact map. Day 1 evidence remains unchanged.
- Updated README, PLAN, SPEC, RESEARCH, HANDOFF, CLAUDE, ENVIRONMENT, DECISIONS,
  WINDOWS_SETUP and STATUS. `docs/OWNER_CONTEXT.md` retains the original paste context.

## Checks actually run

1. `work/v2/Scripts/python.exe scripts/verify_mcp.py` — **PASS: 82 checks / 27 calls**.
   Real SDK STDIO clients, real server and real LibrePCB. Legacy protocol
   `2025-11-25`; automatic discovery `2026-07-28`. All five tools, complete
   pagination, structured errors, bounded wire responses, containment, saved-state
   invariants, source/copy changes, locks/recovery, missing CLI and negative
   designs passed. Missing embedded device data was rejected by LibrePCB itself.
   All **184 source files unchanged**. Run: `work/d2-2767e3/`.
2. `.venv/Scripts/python.exe scripts/verify_codex_host.py --codex <recorded path>`
   — **PASS: 7 checks** using installed **codex-cli 0.153.4**. All five tools and
   an outside-root rejection passed. Source preserved; final host stderr empty.
   Run: `work/cx-5134f6/`. This is a direct host test, not UI/model/Claude verification.
3. `work/v2/Scripts/python.exe -m unittest discover -s tests -v` — **19 passed**
   in 21.146 seconds. Actual Windows junction and hardlink rejection included.
   Process timeout testing uses Python subprocesses, not a LibrePCB hang fixture.
4. Fresh venv: hash-verified install of 36 dependencies, editable package install
   with `--no-deps --no-build-isolation`, and `pip check` — **passed**.
5. Updated bootstrap with existing prerequisites — **passed**. Fresh-machine
   LibrePCB installation and a user-followed quickstart are still Day 6 work.
6. Demo/config generation — passed; TOML parsed successfully. Claude Desktop
   config is documentation-based, not an actual Claude connection test.
7. Whitespace, metadata/evidence consistency and handoff-link checks were run
   during final review. Inspect the local checkpoint for the final file set.

Day 1's 13-check / 8-invocation CLI baseline remains valid recorded history in
`evidence/2026-09-10-day1/`; it was not rerun in Day 2. Its source preservation,
ERC/DRC and PNG/PDF/Gerber results do not complete the upcoming MCP export gate.

## Failures resolved and limits retained

- Deep Windows paths failed initial extraction; shortened run/session/snapshot
  names and explicit generated-path limits resolved this without registry edits.
- Editable build initially lacked `editables`; it is now explicitly pinned and
  the fresh install passes. Report parsing now uses explicit UTF-8.
- Verified v2 SDK imports after an unsuccessful exploratory transport import.
- Fixed the optional Codex test's config-key quoting. An early run inherited an
  unrelated Cloudflare plugin's authentication warning; final process-local
  feature flags disable other plugins/apps, and the final stderr is empty.
- No known failing assertion remains. Supported parser data is a read-only
  projection; geometry, display-value evaluation and serialization are not implemented.
- Saved revision checks assume cooperative local file access, not an atomic
  transaction against an adversarial concurrent writer. Raw logs/snapshots have
  no retention policy; source size, response size, parser work and CLI time are bounded.
- Claude, graphical UI rendering, GUI save/reopen, personal designs, owner review,
  edits, rollback and fresh-machine installation remain unverified.

## Running processes / incomplete operations

Process inspection found no project-owned MCP server, LibrePCB or Codex host-test
process left running. No download or test is pending. Unrelated existing desktop
sessions were not stopped. No automation, publication, deployment, model turn or
account credential change was performed. The Git repository is local with no remote.

## Next task — Claude starts Day 3 here

1. Read AGENTS, this STATUS, PLAN, SPEC, `docs/DAY2.md`, `docs/DECISIONS.md`,
   `docs/ENVIRONMENT.md` and both evidence READMEs. Inspect Git before editing.
   Reuse `.venv`, pinned SDK 2.2.0 and the portable CLI; do not restart setup.
2. Add `run_checks` as a fixed domain operation on a validated saved handle/copy.
   Reuse the working CLI adapter, containment/lock/revision checks and finite
   timeout. Parse stdout counts and stderr findings conservatively. Distinguish
   approved/unapproved findings from parse failures, process failures and timeouts.
   Exit 1 alone is not sufficient; unknown output must never imply a clean design.
3. Add a constrained preview/output path using server-owned, verified output jobs.
   Reuse `resources/preview-jobs.lp`. Enforce allowed output directories, supported
   job types, substitution/path handling, collision policy and artifact limits.
   Do not expose arbitrary project jobs or raw CLI argv to the model.
4. Create disposable fixtures with real ERC and DRC faults; compare summaries to
   raw CLI output. Include the existing 2 ERC / 16 DRC approvals in baseline reports.
5. Exercise the complete MCP read -> checks -> preview/export flow through a real
   client. Verify source preservation and check whether the chosen client can
   actually consume the generated PNG preview. Direct CLI export success is insufficient.
6. Preserve raw diagnostics and bounded structured results. Extend the current
   acceptance harness and save exact evidence. Keep transport/domain/adapters separate.
7. Update STATUS and HANDOFF before stopping. No edit tools until Day 3 passes;
   Day 4's one-value candidate edit still requires reopen/save/reopen, invariants,
   checks comparison, visual inspection and rollback evidence.

## Context and nonblocking owner decisions

Owner authorized starting the project, completing Day 2, and then handing to
Claude. One writer at a time; original conversation and useful links are recorded
in `docs/OWNER_CONTEXT.md`. Follow the startup message in HANDOFF.md.

A public software license, exact Claude client, personal trial design and owner
availability remain undecided. They do not block Day 3. This server uses no
subscription credentials or model API keys.
