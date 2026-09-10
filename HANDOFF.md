# ChatGPT ↔ Claude handoff

## Shared rules

Use this folder as the source of truth. Only one client edits it at a time. Stop outstanding write operations before handing over. Tool calls and running processes do not transfer with a chat transcript.

Both clients should read `AGENTS.md`, `STATUS.md`, `PLAN.md`, and `SPEC.md` at the start. `CLAUDE.md` points to the same instructions. Do not assume automatic discovery; explicitly attach/read these files if necessary.

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

Read AGENTS.md, STATUS.md, PLAN.md, SPEC.md and HANDOFF.md. Inspect the actual files and Git state if available. Follow the next task in STATUS.md and work within the week-one scope. Treat research claims as untested until verified in the pinned environment. Preserve existing work, use one writer at a time, and update STATUS.md with changes, test evidence and the next task before ending. Do not publish or deploy without an explicit request.
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
