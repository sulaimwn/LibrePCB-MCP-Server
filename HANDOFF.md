# Project continuity and client handoff

## Shared rules

Use this folder as the source of truth. Only one client edits it at a time. Stop outstanding write operations before handing over. Tool calls and running processes do not transfer with a chat transcript.

Both clients should read `AGENTS.md`, `STATUS.md`, `PLAN.md`, and `SPEC.md` at the start. `CLAUDE.md` points to the same instructions. Do not assume automatic discovery; explicitly attach/read these files if necessary.

## Current handoff packet

- `docs/OWNER_CONTEXT.md`: owner preferences, authorization and useful conversation links.
- `docs/ENVIRONMENT.md`: exact interpreter/binary locations, versions, Git ownership workaround.
- `docs/WINDOWS_SETUP.md`: setup and repeatable validation commands.
- `docs/DECISIONS.md`: verified CLI traps, implementation boundaries and decisions.
- `docs/DAY2.md`: historical inspection contract and parser subset.
- `docs/DAY3.md`: eight default checks/export/image tools.
- `docs/DAY4.md`: opt-in ninth typed-resistance candidate tool, save/reopen, invariants, rollback and lifecycle.
- `docs/DAY5.md`: deadlines, cancellation, failed reports and recovery.
- `evidence/2026-09-12-day5/README.md`: current 57-test suite, real reliability and all packaged regressions.
- `evidence/2026-09-11-day4/README.md`: historical 42-test, 103-check SDK, 82-check inspection, 15-check Codex host, GUI and package evidence.
- `evidence/2026-09-11-day3/README.md`: 33 unit tests, 82 inspection checks, 73 check/export/image checks, 12 Codex host checks and packaged-server evidence.
- `evidence/2026-09-10-day2/README.md`: 82-check SDK run, seven-check installed Codex host run, 19 tests and dependency evidence.
- `evidence/2026-09-10-day1/README.md`: results, failures encountered, raw-log map, remaining gaps.
- `evidence/2026-09-10-day1/baseline.json`: eight real CLI command records and 13 passing assertions.
- `toolchain.json`, `requirements.lock`, `pyproject.toml`: pinned LibrePCB/fixture, MCP SDK 2.2.0 and hash-locked Windows/Python 3.12 dependencies.

Days 1–5 are finished. **Next is Day 6 installation/user-workflow trial at STATUS.md.**
The owner chose Codex to continue and asked for regular GitHub pushes. No Claude
handoff is planned; keep this packet for continuity.
Do not repeat downloads or replace the working SDK imports. No background server
is required; hosts start STDIO processes when needed. Ready sample and generated
Codex/Claude Desktop configuration snippets are in `work/demo-4a5686/` (experimental edits enabled); no live
client config was changed. Recreate them with `scripts/prepare_demo.py` if needed.

The private GitHub repository is `https://github.com/sulaimwn/LibrePCB-MCP-Server`, remote `origin`, branch `master`. The owner explicitly requested this upload with a WIP README. Downloaded runtimes, environments and scratch artifacts remain ignored. Git commands from the normal user may need a per-command `-c safe.directory=<absolute repository path>` because the sandbox account created `.git`. See the recorded environment; avoid a global wildcard trust setting. Git writes may still require the coding client's permission flow.

## Before switching

1. Save files and record any running processes or incomplete operations.
2. Update STATUS.md: completed changes, actual tests, failures, blockers, next concrete action.
3. If Git has been initialized, review changes and make a focused local checkpoint when appropriate. Do not silently stash, discard or overwrite another session's work.
4. Record exact commands and environment details needed to reproduce a failure. Remove secrets and personal data from reports.
5. Paste the startup message below into the next client. If it lacks folder access, transfer the updated folder and recent status first.

## Startup message

```text
We are building LibrePCB MCP Server. Continue the existing project rather than starting over.

Project folder:
C:\Users\vboxuser\Documents\Codex\2026-09-10\help-me-write-a-good-prompt\outputs\librepcb-mcp-server

Read AGENTS.md, STATUS.md, PLAN.md, SPEC.md, HANDOFF.md, docs/DAY2.md and docs/DAY3.md. Inspect files and Git. Read docs/DAY4.md and docs/DAY5.md too. Days 1–5 are complete: eight default inspection/check/export tools plus an opt-in ninth typed-resistance candidate tool, verified with SDK 2.2.0, the Codex host and LibrePCB 2.1.1. Actual GUI save/reopen, invariant checks and discard/reopen rollback passed for R17. Cooperative cancellation/deadlines and failed-report recovery passed real tests. Continue Day 6 setup/user-workflow trial from STATUS.md; the owner wants Codex to continue and regular GitHub pushes. Reuse .venv and portable CLI. Preserve sources, use one writer, and update STATUS with actual evidence before stopping. No edit tool is a release candidate until its reopen/save/reopen, invariant, check, visual and rollback gates pass. Existing private GitHub publication was owner-requested; do not expand to a public release or deployment without a request.
```

## End-of-session record template

```text
Date/time and client:
Milestone:
Files changed:
Implemented behavior:
Commands/tests actually run and outcomes:
Manual LibrePCB checks performed:
Known failures and unverified assumptions:
Running processes / unfinished operations:
Next concrete action:
Local commit, if any:
```

Keep the latest actionable record in STATUS.md. Add longer session history under `evidence/` when there is actual implementation evidence. A model's statement that something “should work” is not a test result.
