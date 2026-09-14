# Current project status

Updated September 14, 2026, America/Toronto. **Codex remains the active writer.**
The owner said to keep going, maintain context and push regularly. No Claude
handoff is planned. Use these milestone names, not elapsed calendar days.

## Milestone

**Days 1–5 complete. Day 6 installation and user-workflow trial is in progress.**
Package **0.1.0.dev6** is being prepared; Windows x64 / Python 3.12.14 / MCP SDK 2.2.0 /
LibrePCB 2.1.1, stable format 2, revision 06465bf. Dependency lock unchanged.
The server remains WIP: eight tools by default, with opt-in ninth
`create_value_edit`. No general editing, native GUI API, placement or routing.

GitHub: [sulaimwn/LibrePCB-MCP-Server](https://github.com/sulaimwn/LibrePCB-MCP-Server),
**private**, `origin`, branch `master`. Regular pushes are owner-authorized.
Day 4 completed at `ebbd277`; initial Day 5 implementation was pushed as `79040fe`.
The final current checkpoint is identified by `git log -1`. This is development
publication, not a public software release or deployment.

## Day 5 changes

Day 6 work in progress: a fresh private GitHub clone at
`C:/Users/vboxuser/AppData/Local/Temp/lp-d6-425da4/LibrePCB trial` started with no
venv or runtime. Windows PowerShell's default Restricted policy blocked the old
quickstart; a process-only RemoteSigned retry began but its download was aborted
at 77,283,328 bytes. Both failures are retained. The installer now checks Python
first, downloads into a separate partial file, verifies before accepting it, uses
basic parsing/quiet progress, validates exact CLI version and restores Qt settings.
A final clean-checkout rerun and generated-config workflow are still required.
The completed evidence below remains Day 5's historical record.

- `operations.py`: cooperative request budget, shared by nested CLI/domain work.
  The budget includes waiting for the writer lock and project-file loops. Default
  90 seconds, or 240 with experimental editing; `--operation-timeout` can select
  a positive finite limit up to 600 seconds. Per-CLI default remains 30 seconds.
- `server.py`: worker cancellation uses verified AnyIO callbacks; it does not
  abandon a thread that is still writing. `service.py` prevents expired/cancelled
  queued work from starting and removes new handles/registrations on failure.
- CLI/file adapters: checkpoints during file capture/copy and process waits;
  direct-child kill/reap on cancellation or timeout. Flush bounded logs and stop
  the child if log storage fails. No process-tree adapter was added.
- `adapters/reports.py`: exclusive report creation with linked-path rejection.
  Candidate operations record `started.json`, require final `edit.json` storage,
  and retain a separate `failure.json` where possible. Failed report storage cannot
  mask the original failure. Rule-check and unexpected-error diagnostics also cope
  with storage failure. Retries preserve all previous operation directories.
- Edits require capacity for both baseline/candidate check operations before saving.
  The existing typed-resistance scope, exact byte invariants and opt-in gate remain.
- `tests/test_reliability.py`: 15 added tests for budgets, cancellation, writer
  queueing, real subprocess/log failures, failed reports, retry and registration
  cleanup. Synthetic fault cases are labeled; real LibrePCB acceptance is separate.
- `scripts/verify_day5.py`: actual interrupted CLI invocation, report-write failure
  after native validation, successful retries, real MCP active/queued cancellation,
  recovery and restart. README, setup, plan/spec, continuity and evidence updated.

## Checks actually performed

Final integration rows below use the **noneditable Day 5 wheel** installed in
`work/v2`; module loading from site-packages was verified. Unit tests use `.venv`.

| Run | Result and path |
| --- | --- |
| Unit/adapter suite | **57 passed**, 160.095 seconds; `work/day5-unit-final.txt`. |
| New real CLI/MCP reliability | **38 checks / 7 completed MCP calls**, plus two cancelled requests and **26 observed direct service CLI invocations**; `work/d5-de8a3e/`. |
| Existing inspection regression | **82 checks / 27 calls passed**; `work/d2-d6a048/`. |
| Checks/export/native-image/fault regression | **73 checks / 20 calls passed**; `work/d3-4a5bd3/`. |
| Candidate/edit/rollback regression | **103 checks / 30 calls passed**; `work/d4-482d14/`. |
| Installed Codex host | **15 checks / 13 calls passed** with experimental edits; `work/cx-b86578/`. Direct ephemeral calls; no model turn. |
| Package/dependencies | Noneditable wheel `work/day5-wheel/librepcb_mcp_server-0.1.0.dev5-py3-none-any.whl`; both environments passed `pip check`. |
| Final consistency review | **47 checks passed**: source/wheel match, pinned hashes, evidence counts/artifacts, docs links and unchanged earlier evidence. |

All final server/host stderr files are empty. Exact reports, mapped raw CLI logs,
started/failure/success records and wheel hashes are under
`evidence/2026-09-12-day5/`. Earlier editable recovery also passed 38 checks at
`work/d5-b9ab7c/`; the final packet uses the installed run above as authoritative.

The CC0 fixture remains 97 components, 48 nets, one board, two sheets and 184
untouched source files. Validated R17 candidates retain 2 approved ERC / 16 approved
DRC findings and zero unapproved findings; saved controls/candidates have 188 files.
Day 4's actual GUI save/reopen screenshots remain historical visual proof. GUI
was not rerun for reliability changes. Day 5 reran native preview/export delivery,
real rule-fault detection, exact candidate invariants and actual rollback.

## Failures exercised and resolved

- Interrupted one real CLI `--save` invocation with a deliberate 10 ms timeout.
  It failed with retained logs/control and no candidate handle. The source stayed
  unchanged. This does not identify which internal save phase was reached.
- Injected final report-write failure after actual successful LibrePCB candidate
  validation. The tool failed, removed its handle, retained failure evidence and
  then successfully retried into a new directory, preserving earlier outputs.
- Cancelled an active and queued edit through real SDK STDIO requests. The active
  request recorded cancellation, the queued request never started, and subsequent
  source inspection and a same-session edit retry succeeded. Restart rejected old
  handles and reopened the original source unchanged.
- Initial combined unit run had 56 passes and one test KeyError: the test expected
  `process_outcome` inside an interpreted check, which stores timeout in
  `diagnostic_notes`. Corrected the assertion; final 57-test suite passed.

## Boundaries and recovery

See `docs/DAY5.md` for operation budgets, cancellation, retained files and recovery.
Deadlines are cooperative, not atomic or hard real-time: an individual stalled
filesystem call or cleanup can exceed the nominal budget. General descendant
supervision and forced server-process termination remain unsupported. Confirm
owned LibrePCB processes have exited before cleaning an abruptly ended session.
Automatic retention and runtime disk quotas remain deferred; preserve wanted
candidates and clean only inactive, known session directories manually.

Only closed saved projects and the documented typed-resistance shape are supported.
Candidate handles expire with the server session or external saves; copy a closed
candidate to an allowed project folder for later-session use. No source replacement
or model-facing deletion tool exists. No electrical-correctness claim is made.

Fresh-machine setup, owner/personal-design trial, persistent MCP UI installation,
Claude connection and a server license choice remain open. Existing isolated-env
wheel tests do not establish a fresh-machine installation. No subscription keys,
model API calls, credential changes, maintainer contact, automation or deployment.

## Running processes

All Day 5 test harnesses have completed. No owned MCP server, LibrePCB CLI or GUI
process remains running. Other desktop sessions were not stopped. Generated demo
snippets at `work/demo-4a5686/` remain available; no persistent client config changed.

## Next task — Day 6, Codex continues

1. Read AGENTS/STATUS/PLAN/SPEC, `docs/DAY5.md`, environment/setup notes and current
   evidence; inspect Git. Reuse the pinned portable runtime and dependency lock.
2. Follow the Windows quickstart from a clean checkout/environment, checking the
   bootstrap and generated config/sample paths as a user would. Keep this distinct
   from a fresh-machine claim if the same Windows machine is used.
3. Package and walk through open → inspect → checks → native preview → PDF/export;
   optionally demonstrate the narrowly supported candidate edit. Prepare concrete
   artifacts and a reviewable client configuration before an owner trial.
4. Record any actual installation failures, exact commands and recovery. Keep the
   WIP/experimental gates and source preservation. A second client is optional;
   the owner deferred Claude. Continue meaningful GitHub pushes.
5. Owner review and license choice remain release gates. Day 7 is a local release
   candidate only when its gates pass. No native-fork expansion during packaging.
