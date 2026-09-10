# ChatGPT ↔ Claude handoff

## Shared rules

Use this folder as the source of truth. Only one client edits it at a time. Stop outstanding write operations before handing over. Tool calls and running processes do not transfer with a chat transcript.

Both clients should read `AGENTS.md`, `STATUS.md`, `PLAN.md`, and `SPEC.md` at the start. `CLAUDE.md` points to the same instructions. Do not assume automatic discovery; explicitly attach/read these files if necessary.

## Current handoff packet

- `docs/OWNER_CONTEXT.md`: owner preferences, authorization and useful conversation links.
- `docs/ENVIRONMENT.md`: exact interpreter/binary locations, versions, Git ownership workaround.
- `docs/WINDOWS_SETUP.md`: setup and repeatable validation commands.
- `docs/DECISIONS.md`: verified CLI traps, implementation boundaries and decisions.
- `docs/DAY2.md`: actual five-tool contract, parser subset, SDK APIs, limits and client-test boundaries.
- `evidence/2026-09-10-day2/README.md`: 82-check SDK run, seven-check installed Codex host run, 19 tests and dependency evidence.
- `evidence/2026-09-10-day1/README.md`: results, failures encountered, raw-log map, remaining gaps.
- `evidence/2026-09-10-day1/baseline.json`: eight real CLI command records and 13 passing assertions.
- `toolchain.json`, `requirements.lock`, `pyproject.toml`: pinned LibrePCB/fixture, MCP SDK 2.2.0 and hash-locked Windows/Python 3.12 dependencies.

Days 1 and 2 are finished. **Resume Day 3 at STATUS.md: MCP checks and previews.**
Do not repeat downloads or replace the working SDK imports. No background server
is required; hosts start STDIO processes when needed. Ready sample and generated
Codex/Claude Desktop configuration snippets are in `work/demo-bf2ee7/`; no live
client config was changed. Recreate them with `scripts/prepare_demo.py` if needed.

The Git repository is local, with no remote. Git commands from the normal user may need a per-command `-c safe.directory=<absolute repository path>` because the sandbox account created `.git`. See the recorded environment; avoid a global wildcard trust setting. Git writes may still require the coding client's permission flow.

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

Read AGENTS.md, STATUS.md, PLAN.md, SPEC.md, HANDOFF.md and docs/DAY2.md. Inspect the actual files and Git state. Days 1 and 2 are complete: five read tools work with SDK 2.2.0 and the installed Codex host against LibrePCB 2.1.1. Continue Day 3's checks/previews from STATUS.md. Reuse the existing .venv and portable CLI. Keep source designs unchanged, use one writer at a time, and update STATUS.md with changes, actual test evidence and the next task before ending. No edit tool until the read/check/export MCP gate passes. Do not publish or deploy without an explicit request.
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
