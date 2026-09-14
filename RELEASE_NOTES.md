# LibrePCB MCP Server 0.1.0rc1 — local candidate

**WIP local candidate. No public release.** Candidate-specific acceptance is
recorded separately against the bundle hash and source revision.
The owner chose to leave the server license undecided for now and accepted the Day 6 sample
REVIEW.md on September 14, 2026; this does not establish a personal-design,
owner-followed installation or persistent live-chat trial.

## Supported and tested combination

Windows 11 x64 (recorded build 26200), Python 3.12.14, MCP Python SDK 2.2.0,
LibrePCB 2.1.1 with stable file format 2 / revision 06465bf. Installed Codex
0.153.4 has been tested through direct ephemeral MCP host calls. All 36 runtime
and build dependencies remain hash-pinned in requirements.lock.

## Available behavior

Eight default tools inspect closed saved projects, summarize components/nets,
run electrical and board-rule checks, attach native schematic PNGs and export
schematic PDF or fixed Gerber/Excellon output jobs. Inputs are restricted to
configured local roots; results identify saved snapshots and retained artifacts.

The optional ninth tool creates a separate candidate for one existing resistor's
typed RESISTANCE value. It validates native save/reopen, exact file invariants
and matching checks, and preserves the source. Only the documented simple
resistance shape, one board and zero unapproved findings are accepted.

## Validation carried forward

The runtime behavior is unchanged from dev6 except its version. Day 6 verified
fresh GitHub setup on this Windows machine, repeat setup preserving 1,258 demo
files, 57 unit/adapter tests, and generated-config workflows including the
noneditable wheel. The owner has now accepted the prepared output review.

Day 5 verified the complete packaged inspection/export/edit/reliability suites
and Codex host; Day 4 established real LibrePCB GUI save/reopen and rollback.
Those historical packets remain unchanged. Day 7 candidate-specific results
are recorded separately; building a bundle alone is not runtime acceptance.

## Known limits and remaining work

- Only this Windows/Python/LibrePCB combination and the included CC0 sample are
  verified. A fresh Windows installation and arbitrary personal designs are not.
- No live unsaved editor state, general editing, component insertion, placement,
  wiring, routing or native LibrePCB API. Claude connection is untested.
- Generated snippets do not install a persistent client connection. Existing
  host tests use direct tools and do not exercise an AI model turn or live UI.
- Checks are compatibility evidence, not electrical or manufacturing approval.
- Cancellation/deadlines are cooperative. Direct children are supervised;
  forced server termination and descendant process-tree cleanup are not guaranteed.
- Snapshots, failed attempts, wanted candidates and logs are retained. Clean only
  known inactive directories manually; no automatic quota or retention service.
- Source replacement and chained candidate edits are unsupported. Handles expire
  with the server session or external saves; reopen a closed copy in an allowed root.
- The software license choice and any public release decision remain with the owner.

## Install, verify and recover

The source archive contains README.md, docs/WINDOWS_SETUP.md and
docs/OWNER_TRIAL.md. Bootstrap the pinned prerequisites, install the included
wheel if testing the package, and run prepare_demo.py --verify. The optional
--experimental-edits flag exercises the candidate workflow. Keep existing client
configuration when adding the generated entry.

A failed candidate does not replace the original. Retain its diagnostics and use
a fresh attempt after resolving the reported condition. Roll back a successful
experiment by closing/discarding its separate copy and reopening the original.
Detailed lifecycle and recovery guidance is in docs/DAY4.md and docs/DAY5.md.

LibrePCB and Python dependencies are downloaded separately, not bundled. The
D0 reader fixture is CC0-1.0 by U. Bruhin; its license/provenance is in
tests/fixtures/. This local bundle grants no new license to third-party content.
