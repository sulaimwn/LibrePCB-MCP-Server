# Current project status

Updated September 11, 2026, America/Toronto. **Codex remains the active writer.**
The owner requested Day 4 and necessary supporting work, regular GitHub pushes,
and no near-term Claude handoff. Keep the continuity files current regardless.

## Milestone

**Days 1–4 complete. Next: Day 5 reliability work.** Package **0.1.0.dev4**.
Windows x64 / Python 3.12.14 / MCP SDK 2.2.0 / LibrePCB 2.1.1, stable format 2.
The server remains WIP. Eight inspection/check/export tools are enabled by default;
`--enable-experimental-edits` adds a ninth, `create_value_edit`.

The new tool creates a separate typed-resistance candidate, validates real CLI
strict-open/save/reopen, preserves all other design bytes, and compares ERC/DRC
against the source. It checks expected source revision and locks, rejects
unsupported shapes/part choices and unapproved findings, and never replaces the
original. See `docs/DAY4.md` for exact scope, limits and candidate lifecycle.

GitHub: [sulaimwn/LibrePCB-MCP-Server](https://github.com/sulaimwn/LibrePCB-MCP-Server),
**private**, branch `master`, remote `origin`. The owner authorized continuing
pushes. The initial Day 4 GUI/CLI proof checkpoint is `b0079f8`; the final current
checkpoint is identified by `git log -1`. No public release or deployment is claimed.
Source, docs, tests, fixture, evidence and history are uploaded. Runtimes, environments,
scratch copies and credentials remain excluded.

## Implemented and files changed

- `src/librepcb_mcp/adapters/edits.py`: bounded typed-attribute patch, control-save
  initialization checks, and exact full-file candidate invariants.
- `service.py`: opt-in candidate creation, expected/source/candidate revisions,
  saved unedited control, strict/save/strict verification, baseline/candidate
  findings comparison, session limit and failure reports. Returned candidate
  handles work with existing read/check/export tools.
- `server.py`: opt-in ninth tool and launch flag; default tools remain eight.
  Package metadata/version updated to `0.1.0.dev4`; dependency lock unchanged.
- `scripts/verify_value_roundtrip.py`, `verify_day4.py`: real CLI probe and full
  SDK candidate/rejection/export/rollback acceptance. Codex host harness adds
  `--experimental-edits`. `prepare_demo.py` adds matching config generation.
- `tests/test_edits.py`: nine tests for exact scalar changes, unsafe/unchanged
  values, unsupported components/part choices, Unicode, control-save boundaries
  and unrelated design changes. Existing 33 tests retained.
- README, PLAN, SPEC, HANDOFF, CLAUDE, environment/setup/decision/research notes,
  `docs/DAY4.md`, and `evidence/2026-09-11-day4/` updated for continuation.

## Validation actually performed

| Check | Result |
| --- | --- |
| Unit/adapter suite | **42 passed**, 25.669 s, `work/day4-unit-tests.txt`. Synthetic fixtures cover failure modes; actual process/filesystem tests remain included. |
| Existing SDK inspection regression | **82 checks / 27 calls passed**, `work/d2-2ed875/`, editable Day 4 package. |
| SDK candidate/edit/rollback acceptance | **103 checks / 30 calls passed** in both `work/d4-291dd8/` (editable) and `work/d4-b5b753/` (installed wheel). Both reports are retained in the Day 4 evidence packet. |
| Installed Codex host | **15 checks / 13 calls passed**, `work/cx-b6e940/`. All nine tools, validated candidate and native edited image. Stderr empty. |
| Real GUI save/reopen | R17 visibly **1.5 kΩ → 2.2 kΩ**. Actual editor saved candidate, closed, restarted and displayed 2.2 kΩ again. Independent unmodified GUI-saved control comparison passed. |
| CLI strict/save/strict probe | Passed at `work/d4p-89d75/`; reproducible via `scripts/verify_value_roundtrip.py`. |
| Package | Day 4 wheel installed noneditable in existing isolated `work/v2`; site-packages loading verified and full 103-check acceptance passed. `pip check` passed in both environments. |
| Final consistency review | **38 checks passed**: source/wheel match, pinned fixture and dependencies, report counts, artifact links, image hashes, config snippets and unchanged historical evidence. |
| Demo | `work/demo-4a5686/`: unchanged sample and experimental Codex/Claude snippets with 300-second tool timeout. No persistent client configuration edited. |

Fixture remains 97 components, 48 nets, one board and two sheets. Baseline and
candidate keep **2 ERC / 16 DRC approvals**, zero unapproved findings. The tests
preserve all 184 original files. Saved controls/candidates add four editor
preference files (188 total). After equivalent save behavior, only the intended
resistance scalar differs. Main PNG is unchanged; Ethernet changes as expected.
PDF exports work. Gerber/drill files retain identical nonvolatile content; only
creation-time comments and derived checksum comments differ.

Rollback was actually tested: after MCP shutdown, the harness verified and removed
only its closed, known candidate copy, then reopened the original through a fresh
client at 1.5 kΩ. Invalid/stale inputs, locks, occupied candidate directories,
candidate chaining and an actual ERC-fault source were rejected and preserved.

The actual GUI and Codex-delivered edited PNG were visually inspected. GUI test
helpers used a private workspace/config and scoped input to the owned process.
This does not introduce live-editor control into the product. Codex host calls
were direct/ephemeral, without a model turn; Claude and a live chat installation
remain untested. Day 1/2/3 evidence is unchanged historical context.

## Resolved issues and remaining limits

- CLI saving adds `settings.user.lp`; GUI saving fills board-layer visibility.
  Validate against independent saved controls instead of overlooking file changes.
- A Gerber comparison initially failed on the derived MD5 after timestamp changes.
  Only those two metadata fields are normalized in the final comparison.
- An initial part-choice unit fixture modified the wrong shared-device instance;
  selecting R17 by parsed component ID fixed it. Final 42-test suite passes.
- GUI `--help` does not print help; the exploratory process hit its timeout and
  was stopped. Subsequent trials used supported project arguments and isolated
  environment settings. Foreground checks stopped input when focus moved away.
- Editing remains opt-in and narrow: one board, plain decimal typed resistance,
  no populated part choices/extra attributes/chaining. No arbitrary editing,
  placement, wiring, routing or native API bridge. No electrical-correctness claim.
- Candidate handles expire with the session and become stale after external saves.
  Copy a closed candidate into an allowed project folder for later-session use.
- Cooperative revision checks are not atomic filesystem transactions. There is
  no operation-wide deadline, automated retention, runtime disk quota or general
  child-process-tree supervision. Fresh-machine and personal-design trials remain.
- Server license selection and owner trial remain open; the fixture is CC0.

## Running processes and operations

No project test, MCP server, CLI or GUI process remains running. The installed-wheel
run completed successfully. Final checks and publication are recorded in the Day 4
evidence packet and current Git checkpoint. No model API calls, subscriptions,
credential changes, maintainer contact, deployment, automation or persistent MCP
client-config change was performed. Other desktop sessions were not stopped.

## Next task — Day 5 reliability, Codex continues

1. Read AGENTS, STATUS, PLAN, SPEC, `docs/DAY4.md`, DECISIONS, ENVIRONMENT and
   Day 4 evidence; inspect Git. Reuse `.venv`, portable LibrePCB and SDK 2.2.0.
   One writer at a time; continue regular meaningful pushes to the same repo.
2. Harden the existing nine-tool scope: interrupted/failed candidate save or
   report storage, cumulative deadlines, stale/locked candidates, retained partial
   artifacts, operation limits and recovery. Preserve source and existing output.
3. Reproduce failures with bounded tests and real CLI where relevant. Do not
   expand to placement/routing or native bindings during this reliability milestone.
4. Keep experimental edits disabled by default. Document retention and clean
   shutdown behavior before broader trials. Owner deferred switching to Claude;
   keep handoff docs ready, but do not require a second client to make progress.
5. Day 6 remains fresh-machine/setup workflow and owner review; Day 7 is a release
   candidate only if its gates pass. Native GUI API investigation is after the
   initial milestones, beginning with one footprint-pad move/undo experiment.
