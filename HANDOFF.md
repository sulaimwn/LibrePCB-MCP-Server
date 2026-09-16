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
- `docs/DAY6.md`, `docs/OWNER_TRIAL.md`: fresh setup, generated configuration and owner review.
- `docs/DAY7.md`, `RELEASE_NOTES.md`, `CHANGELOG.md`: completed local rc1 candidate.
- `evidence/2026-09-15-live-chat/README.md`: actual connected Codex model-led sample workflow; all eight default tools, native image, PDF and unchanged source.
- `evidence/2026-09-14-day7/README.md`: exact tested candidate hashes, 30 package checks, SDK and host acceptance.
- `evidence/2026-09-14-day6/README.md`: current installation, repeat setup, 57-test and installed-wheel walkthrough evidence.
- `evidence/2026-09-12-day5/README.md`: current 57-test suite, real reliability and all packaged regressions.
- `evidence/2026-09-11-day4/README.md`: historical 42-test, 103-check SDK, 82-check inspection, 15-check Codex host, GUI and package evidence.
- `evidence/2026-09-11-day3/README.md`: 33 unit tests, 82 inspection checks, 73 check/export/image checks, 12 Codex host checks and packaged-server evidence.
- `evidence/2026-09-10-day2/README.md`: 82-check SDK run, seven-check installed Codex host run, 19 tests and dependency evidence.
- `evidence/2026-09-10-day1/README.md`: results, failures encountered, raw-log map, remaining gaps.
- `evidence/2026-09-10-day1/baseline.json`: eight real CLI command records and 13 passing assertions.
- `toolchain.json`, `requirements.lock`, `pyproject.toml`: pinned LibrePCB/fixture, MCP SDK 2.2.0 and hash-locked Windows/Python 3.12 dependencies.

Days 1–6 are finished for the included sample. **The owner accepted its output
review. Day 7's local rc1 candidate also passes; continue from STATUS.md.** The owner chose
to leave the license undecided; this permits the private local trial, not public
software release. The actual Codex live-chat sample workflow passed September 15;
personal-design trials remain unverified. Editing is disabled in that connection.
The owner chose Codex to continue and asked for regular GitHub pushes. No Claude
handoff is planned; keep this packet for continuity.
Do not repeat downloads or replace the working SDK imports. No background server
is required; hosts start STDIO processes when needed. Ready sample and generated
Codex/Claude Desktop configuration snippets are in `work/demo-e8a9b4/` (experimental edits enabled).
The live Codex connection uses the default sample `work/demo-d9c0ce/`; its active
session is `d/s-c0bf9bf17d48/`. Preserve it while the chat is using it. This
walkthrough did not edit client settings. Recreate sample snippets with
`scripts/prepare_demo.py` if needed.

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

Read AGENTS.md, STATUS.md, PLAN.md, SPEC.md, HANDOFF.md, docs/DAY2.md and docs/DAY3.md. Inspect files and Git. Read docs/DAY4.md and docs/DAY5.md too. Days 1–5 are complete: eight default inspection/check/export tools plus an opt-in ninth typed-resistance candidate tool, verified with SDK 2.2.0, the Codex host and LibrePCB 2.1.1. Actual GUI save/reopen, invariant checks and discard/reopen rollback passed for R17. Cooperative cancellation/deadlines and failed-report recovery passed real tests. Day 6 fresh-checkout setup, repeat setup and installed-wheel walkthroughs now pass; read docs/DAY6.md and its evidence. Owner review of work/demo-e8a9b4/review-fb79f0/ was accepted. Day 7 local rc1 candidate passes 30 package checks, both sample workflows and the Codex host; read docs/DAY7.md and its evidence. The owner leaves the license undecided. Continue client usability and broader inspection from STATUS.md; the owner wants Codex to continue and regular GitHub pushes. Reuse .venv and portable CLI. Preserve sources, use one writer, and update STATUS with actual evidence before stopping. No edit tool is a release candidate until its reopen/save/reopen, invariant, check, visual and rollback gates pass. Existing private GitHub publication was owner-requested; do not expand to a public release or deployment without a request.
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
