# Day 5: reliability and recovery

Implementation in progress, September 11, 2026. Windows x64, Python 3.12.14,
LibrePCB 2.1.1 and MCP SDK 2.2.0 remain pinned. This milestone hardens the
existing eight default tools and opt-in ninth tool; it adds no design features.

## Whole-operation time budgets

The server now enforces one cooperative deadline across writer-lock queueing,
project-file loops and sequential CLI calls. The default is 90 seconds with
inspection tools, or 240 seconds when experimental editing is enabled.
`--operation-timeout` accepts a positive finite number up to 600 seconds.
`--timeout` remains the independent per-CLI limit (30 seconds by default).
The earlier limit wins. Status exposes both settings.

MCP hosts should allow time for cleanup after the server deadline. Generated
Codex snippets allow 120 seconds by default and 300 with experimental editing.
Increase that host limit if you explicitly increase the server budget.

The operation budget starts when the worker enters dispatch. Waiting for the
single writer uses short interruptible waits; a timed-out or cancelled queued
edit cannot acquire that lock later and start writing. Filesystem calls are
cooperative boundaries, not interruptible kernel transactions. A stalled disk
or process cleanup may exceed the nominal deadline; this is not a hard real-time
guarantee. Independent adapter use without a dispatch scope retains its CLI timeout.

## Cancellation and storage failures

Transport workers check AnyIO's cancellation signal without abandoning their
threads. Cancellation during project copying or a running CLI stops at a
checkpoint; the direct CLI child is killed and reaped, diagnostics are closed,
and the writer lock is released. No subsequent validation or candidate publication
is allowed for that failed request. New handles/artifact registrations are removed
if an operation fails. Existing handles and previous artifacts are preserved.

This uses verified installed AnyIO and MCP SDK interfaces. The SDK sends
`notifications/cancelled` when a request is abandoned, and suppresses the reply
to the cancelled request. A following tool call can inspect the preserved source.
Cancellation is not a guarantee that a request which already completed is undone;
its separate candidate can remain in the data directory.

Edit operations write `started.json` before native validation. A completed
candidate requires successful `edit.json` storage. Failure removes the temporary
handle and attempts a separate `failure.json`; an error storing that report is
reported alongside the original error, without claiming an artifact exists.
Report writes use exclusive creation and reject linked paths. Existing reports
and operation directories are preserved. A partial report from an I/O failure
must not be treated as evidence of a valid candidate.

Rule-check failure reporting and unexpected-error diagnostics also preserve the
primary error if storage fails. CLI log writers flush their bounded output and
stop the direct child promptly when a write fails, instead of waiting for its
full timeout. Edits require room for both baseline and candidate check operations
before starting a save.

## Recovery and retained artifacts

After a normal completion/cancellation/timeout, use a fresh call to inspect the
original handle. After a server restart, reopen the original path: all old handles
expire. An edit retry reserves a new directory; partial files are never reused.
An incomplete candidate is not a validated design. Keep the original source and
review the retained diagnostic/failure files before deciding what to do with it.

Snapshots, controls, candidates, logs and exports remain under the configured data
root. Automatic retention/deletion is intentionally deferred: the server cannot
know which candidate the owner wants to keep. Once the owning server and LibrePCB
processes have exited, copy any wanted candidate to an allowed project folder,
then remove only the inactive session directories you no longer need. Do not
remove `.lock`, recovery data or files still used by another process.

Direct-child cleanup is the supported boundary. General descendant supervision
and forced server-process termination are not solved by cooperative cancellation.
If a host forcibly kills the server, confirm its LibrePCB process has also exited
before touching retained copies. No process-tree, crash-atomicity, runtime disk
quota, electrical-correctness or fresh-machine guarantee is claimed.

## Verification plan and evidence

`tests/test_reliability.py` injects storage/validation faults and uses real Python
subprocesses for cumulative deadlines, log failure and AnyIO cancellation. These
are adapter tests, not LibrePCB integration evidence.

`scripts/verify_day5.py` invokes the actual CLI with one deliberately short save
timeout, checks preserved sources and partial reports, injects final report-write
failure after real candidate validation, and retries successfully. It also cancels
an active and queued edit through the real SDK/STDIO server, verifies cleanup and
retry in the same session, then verifies old-handle rejection after restart.
The short CLI timeout does not establish which internal save phase was reached.

Existing Day 2 inspection, Day 3 checks/export/fault and Day 4 edit/rollback
harnesses provide regression coverage. Actual run results will be recorded in
`evidence/2026-09-11-day5/` and STATUS before completing this milestone.

Primary sources: [AnyIO worker cancellation](https://anyio.readthedocs.io/en/stable/threads.html#reacting-to-cancellation-in-worker-threads),
plus installed SDK 2.2.0 `mcp/shared/jsonrpc_dispatcher.py` and installed AnyIO
`from_thread.py`, `to_thread.py`, `_backends/_asyncio.py`. Windows process-tree
containment remains separate future work; [Microsoft job-object documentation](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
was reviewed, but no such adapter was added in this milestone.
