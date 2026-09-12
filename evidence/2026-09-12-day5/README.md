# Day 5 — cancellation, deadlines and failure recovery

Work performed September 11–12, 2026; final packet recorded September 12,
America/Toronto. Server **0.1.0.dev5**, Python 3.12.14, Windows x64, LibrePCB
2.1.1 / stable format 2 / revision 06465bf, MCP SDK 2.2.0. WIP development
evidence, not a release or proof of arbitrary-design compatibility.

## Final results

| Verification | Recorded result | Report |
| --- | --- | --- |
| Unit/adapter tests | **57 passed**, 160.095 seconds | [Output](unit-tests.txt) |
| New CLI/MCP reliability | **38 checks**, 7 completed MCP calls, 2 cancelled requests; 26 observed direct service CLI calls | [Reliability](reliability.json) |
| Inspection regression | **82 checks / 27 calls passed** | [Inspection](inspection.json) |
| Checks, exports, native images and actual rule faults | **73 checks / 20 calls passed** | [Exports](exports.json) |
| Candidate edit, invariants and actual rollback | **103 checks / 30 calls passed** | [Edit](edit.json) |
| Installed Codex host | **15 checks / 13 calls passed**, edits enabled | [Host](host.json) |
| Package | Noneditable wheel loaded from site-packages; both environments pass `pip check` | [Build/environment](build-and-environment.json) |
| Final consistency review | **47 checks passed**, including source/wheel equality, hashes, report counts and local links | [Review](final-review.json) |

Every final integration/host report above uses `work/v2/Scripts/python.exe` with
the installed Day 5 wheel. The unit suite uses the editable `.venv`. Counts are
assertions/protocol checks across one fixture and its controlled mutations, not
independent designs. No mock-only test is counted as LibrePCB integration.

## What was exercised

The harness starts with the original CC0 D0 reader: 97 components, 48 nets,
one board, two schematic sheets and **184 unchanged source files**.

1. A real LibrePCB `--save` invocation receives a deliberate 10 ms timeout. It
   fails with a timeout, retained logs/control copy and started/failure records.
   No candidate handle is registered. This proves interruption of an actual
   invocation; it does not identify which internal save phase was reached.
2. A second candidate passes actual CLI save/reopen, exact byte invariants and
   baseline/candidate checks. The developer harness then injects a final report
   storage error. The operation fails and removes its temporary handle; the source
   and diagnostics remain. This is controlled I/O fault injection, not a claim
   that the machine's physical disk filled up.
3. A retry succeeds in a new directory. Both earlier partial operation directories
   remain byte-identical to their state before the retry.
4. The SDK cancels an active edit and another waiting for the writer lock through
   real STDIO requests. The active request records `cancelled`; the queued request
   never starts. A following source read succeeds after cleanup, and a new edit
   succeeds in the same server session without replacing cancelled artifacts.
5. After restart, the old candidate handle is rejected. Reopening the original
   produces the same original revision. All source files remain unchanged.

The 26 directly observed CLI calls cover the first three steps. The MCP portion
also launches real CLI calls; those logs are retained separately, not included in
that direct-call count. Cancelled MCP requests intentionally have no successful
result; seven completed calls are listed in the report.

The regressions additionally verify approved versus unapproved ERC/DRC, deliberate
net/trace faults, invalid/locked/stale/path/collision inputs, PNG/PDF/Gerber output,
the exact R17 scalar change and discard/reopen rollback. Validated candidates keep
**2 approved ERC / 16 approved DRC findings**, zero unapproved findings, and 188
files after verified preference initialization. Actual GUI save/reopen proof is
retained in [Day 4](../2026-09-11-day4/README.md); GUI was not rerun for these
reliability changes. Native image delivery was rerun through SDK and Codex host.

## Artifacts and reproducibility

- [Tool schemas](tool-schemas.json), [build and wheel hashes](build-and-environment.json).
- [Artifact map](artifact-map.json): 268 raw CLI stdout/stderr files and 48
  check/export/started/failure/success reports. `d` is the MCP session root;
  `ds` is the direct service trial root. `<REPO>` replaces the local root path.
- The five top-level server/host stderr files are empty. Per-CLI stderr includes
  deliberately introduced failures and is preserved without hiding them.
- Run [Windows setup](../../docs/WINDOWS_SETUP.md); the new harness is
  `scripts/verify_day5.py`. Full generated exports and scratch copies remain
  ignored under `work/`; the rollback test deliberately discards its candidate.
- [Reliability contract and recovery](../../docs/DAY5.md) explains operation time
  limits, cancellation, report states and manual cleanup.

The first combined unit run had one test error: it looked for `process_outcome`
inside an interpreted check, which records timeouts in `diagnostic_notes`.
Correcting the assertion produced the final **57/57** pass. The initial editable
recovery run also passed 38 checks; this packet uses the final installed run.

## Practical limits

Cancellation/deadlines are cooperative; individual stalled filesystem calls and
process cleanup may exceed the nominal budget. Direct CLI children are supervised.
General descendant handling and forcibly killing the server are outside the
tested guarantee. Retention and runtime disk quotas remain manual/deferred.
No Windows job-object adapter, live editor API or source-overwrite tool was added.

The package used an existing isolated dependency environment, not a fresh Windows
machine. Codex host calls were direct and ephemeral, without a model turn or a
persistent client configuration change. Owner/personal-design trial, clean setup
walkthrough, Claude connection and server license choice remain pending gates.
