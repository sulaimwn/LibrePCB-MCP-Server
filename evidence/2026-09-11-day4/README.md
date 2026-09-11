# Day 4 — verified candidate edit and rollback

Verified September 11, 2026, on Windows x64 with Python 3.12.14,
LibrePCB 2.1.1 / format 2 / revision 06465bf, MCP SDK 2.2.0 and server
`0.1.0.dev4`. This is WIP development evidence, not a software release.

The experimental ninth tool changes one supported typed resistance in a separate
candidate. Eight inspection/check/export tools remain enabled by default.
See [the exact contract and limits](../../docs/DAY4.md).

## Recorded results

| Run | Actual result | Evidence |
| --- | --- | --- |
| Unit/adapter suite | 42 tests passed in 25.669 seconds | [Output](unit-tests.txt) |
| SDK edit and rollback, installed wheel | 103 checks / 30 MCP calls passed; `work/d4-b5b753` | [Report](mcp-edit-rollback.json) |
| Same SDK acceptance, editable package | 103 checks / 30 calls passed; `work/d4-291dd8` | [Report](mcp-edit-editable.json) |
| Existing SDK inspection regression | 82 checks / 27 calls passed; `work/d2-2ed875` | [Report](mcp-inspection.json) |
| Installed Codex host, edits enabled | 15 checks / 13 calls passed; `work/cx-b6e940` | [Report](codex-host.json) |
| Direct real CLI probe | Control save, candidate strict-open, save and strict-reopen passed | [Probe](cli-roundtrip-probe.json) |
| Actual LibrePCB GUI | Candidate displayed 2.2 kΩ, saved, closed and reopened in a new process at 2.2 kΩ | [GUI record](gui-save-reopen.json), [saved](saved-r17.png), [reopened](reopened-r17.png) |
| Package/dependencies | Noneditable wheel loaded from site-packages; both environments passed `pip check` | [Build record](build-and-environment.json) |
| Final consistency review | 38 checks passed; metadata, source/wheel equality, hashes, links and evidence | [Review](final-review.json) |

Counts above are recorded assertions, including protocol/result checks, not counts
of independent designs or test cases. The 42 unit/adapter tests include synthetic
failure fixtures; the SDK, host and GUI rows use real LibrePCB. Day 3's full
73-check suite is historical evidence and was not rerun in this milestone.

## What the edit proved

The CC0 D0 reader fixture has 97 components, 48 nets, one board and two sheets.
R17 changed from **1.5 kΩ to 2.2 kΩ** by replacing only its quoted numeric
RESISTANCE attribute. Its template, unit and identifiers remain intact.

All **184 source files** remain byte-identical. Saving an independent unmodified
control creates four preference files, making 188. After equivalent saves,
the candidate equals that control except the intended scalar: connectivity,
geometry, embedded libraries, jobs, approvals and every other byte are preserved.
CLI validation and the separately GUI-saved control comparison both passed.

Baseline and candidate retain **2 approved ERC / 16 approved DRC findings**, with
zero unapproved findings. Native MCP preview delivery works: Main PNG is unchanged,
Ethernet reflects the edit. PDF and all 11 Gerber/Excellon artifacts export; the
manufacturing comparison permits only creation-date and derived MD5 comments to
differ, preserving all other bytes.

The actual Codex-delivered edited image was visually inspected and is retained
unchanged as [edited-ethernet-mcp.png](edited-ethernet-mcp.png). GUI screenshots
are separate actual-editor evidence, not generated illustrations.

## Rejections and rollback

The SDK acceptance rejects unsafe/unchanged values, unknown component IDs,
stale revisions, source/candidate locks, occupied operation directories,
candidate chaining and a source with an actual newly introduced ERC fault.
Existing lock files, owner files and source data are preserved; failure artifacts
are retained. Tests verify the original source invalidates candidate handles
after a source change, then restore only the test's own mutation.

Rollback is exercised after the MCP process closes. The harness validates the
exact owned candidate path and contents, deletes only that disposable candidate,
then starts a fresh default eight-tool client and reopens the unchanged source
at **1.5 kΩ**. `rollback_completed` and `source_preserved` are true in both
acceptance reports. No model-facing deletion or source-replacement tool exists.

## Artifacts and reproduction

- [Tool schemas](tool-schemas.json), [build/environment hashes](build-and-environment.json).
- [Artifact map](artifact-map.json) maps `<REPO>` diagnostic paths to retained
  `raw/` logs and `reports/` check, export and edit records. Direct probe logs are
  under `probe-logs/`.
- All four retained server/host stderr files are empty. CLI stderr is preserved
  separately for each invocation, including intentional negative cases.
- Full native exports and scratch projects stay in ignored `work/`. The acceptance
  candidate is intentionally absent after successful rollback. Artifact paths in
  reports describe the state at invocation time, not a promise of permanent files.
- Run the commands in [Windows setup](../../docs/WINDOWS_SETUP.md). Use
  `scripts/verify_day4.py` for the SDK workflow and add `--experimental-edits` to
  `scripts/verify_codex_host.py` for the nine-tool host trial.

## Resolved issues and boundaries

Initial strict file comparison exposed newly saved preference files; independent
saved controls resolved this explicitly. GUI save adds board-layer visibility,
so its comparison uses a separately GUI-saved unedited control. Initial Gerber
comparison missed that a timestamp also changes the derived MD5; only those two
metadata fields are normalized now. An early part-choice test mutated another
instance of a shared device; selecting R17's parsed node corrected the test.

GUI `--help` started workspace selection and hit the exploratory timeout. The
successful trials used verified project arguments, isolated workspace/config
paths and input scoped to the owned GUI process. This test helper is not a product
API; no native bridge or live-editor tool has been implemented.

The installed wheel used the existing isolated dependency environment, not a
fresh machine. Codex host testing used direct tools without a model turn or
persistent client configuration change. Claude, personal designs, fresh-machine
setup and owner review remain untested. Editing is opt-in, narrow and experimental;
there is no electrical-correctness or arbitrary-design compatibility claim.
Operation-wide deadlines, interrupted-operation recovery and storage/report
failures are Day 5 work. Server license selection remains open.
