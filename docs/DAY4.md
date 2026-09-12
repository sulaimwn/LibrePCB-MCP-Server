# Day 4: validated resistance candidates

This is the Day 4 checkpoint. See [Day 5](DAY5.md) for current operation deadlines,
cancellation, failure reports and recovery behavior.

Implemented September 11, 2026: package **0.1.0.dev4**, Windows x64 / Python
3.12.14 / MCP SDK 2.2.0 / LibrePCB 2.1.1 (stable format 2). Codex continues
development; the owner requested regular GitHub pushes and no Claude handoff.
This remains a WIP prototype with an experimental editing option.

## Tool and supported scope

Eight inspection/check/export tools remain enabled by default. Launching with
`--enable-experimental-edits` adds a ninth tool:

```text
create_value_edit(project_id, component_id, new_value, expected_revision)
```

It returns a separate validated candidate, never replaces the source, and uses
`readOnlyHint=false`, `destructiveHint=false`. Candidate output includes a new
`project_id` usable with inspection/check/export tools, candidate path/revision,
source revision, exact change, invariants, baseline/candidate findings and an
`edit.json` report. The result explicitly says `experimental=true`.

Current constraints:

- Closed saved source, unchanged expected revision, exactly one board, and no
  unapproved ERC/DRC findings. Approved findings remain present and must match.
- A two-signal non-schematic-only component named like `R17`, raw value exactly
  `{{RESISTANCE}}`, unlocked assembly, and a sole typed RESISTANCE attribute.
- Existing unit must be microohm, milliohm, ohm, kiloohm or megaohm. The tool
  changes the numeric value in that unit; it does not infer or convert units.
- `new_value` is a string: nonnegative plain decimal, at most six fractional
  digits and value at most 1,000,000 in the existing unit. No signs, exponents,
  suffixes, expressions, leading-zero variants, blank values or semantic no-ops.
- Populated part choices and extra component attributes are rejected to avoid
  leaving procurement information inconsistent with a changed resistance.
- At most eight edit attempts after input validation per server session. The
  existing check/export session limits also apply. No candidate edit chaining.

These conditions define a narrow supported shape; they do not establish arbitrary
resistor/library/design compatibility. Only the D0 reader R17 experiment has
real GUI validation. No component insertion, placement, wiring or routing exists.

## Validation sequence and source preservation

1. Recheck source/copy locks and revision, validate the expected revision, parse
   the target and proposed decimal, and reserve a fresh operation directory.
2. Run baseline ERC/DRC on the saved source snapshot; reject unapproved findings.
3. Create a separate unedited control and ask LibrePCB to save it. Every existing
   source file must remain byte-identical. Newly created files may only be the
   expected project/board/schematic `settings.user.lp` preference documents,
   with matching document roots. Other changes stop validation.
4. Copy that saved control into a separate candidate. Replace only the quoted
   resistance scalar using parser character spans, preserving all other UTF-8
   bytes. The raw `{{RESISTANCE}}` template and unit remain unchanged.
5. Run real CLI strict-open, save, and strict-reopen. After each invocation,
   require the full candidate file set to equal the saved control plus that exact
   scalar replacement. This preserves UUIDs, references, signal assignments,
   connectivity, geometry, libraries, approvals, jobs and unknown content.
6. Run candidate ERC/DRC and require matching approved/unapproved counts and
   available finding details. Recheck source and candidate before returning.

Partial failures retain diagnostic/control/candidate files in the new session
directory, with a failure report where possible; failed candidates are not
published as usable handles. Existing output directories are never overwritten.
Source designs are never saved by this operation. Only isolated copies are saved.

The fixture has 184 original files. LibrePCB saving adds four preference files;
the saved control/candidate have 188. GUI saving additionally fills board-layer
visibility preferences. The GUI comparison uses an independently GUI-saved
unmodified control, so no preference changes are silently ignored.

## GUI and MCP evidence

The experiment changed R17 **1.5 kΩ → 2.2 kΩ**. The actual editor displayed 2.2 kΩ,
reported “Project saved!”, closed normally, and a new GUI process reopened the
same value. This agent inspected both displays. After matching control GUI-save
behavior, all 188 candidate files matched the control except the intended scalar.
All 184 original source files remained unchanged.

GUI tests used process-local `LIBREPCB_WORKSPACE` and `LIBREPCB_CONFIG_DIR` under
`work/d4g/`, verified from pinned source, plus the actual `.lpp` argument. Windows
UI Automation and scoped keyboard/mouse input were developer test helpers only;
input stopped unless the owned GUI was foreground. No production GUI adapter or
normal-workspace configuration change was introduced. Embedded project libraries
were sufficient for opening/saving; workspace libraries were not downloaded.

`scripts/verify_day4.py` performs real SDK calls: create candidate, inspect it,
compare all component/net records, rerun checks, receive native images, export PDF
and Gerber/Excellon, reject stale/locked/colliding/unsupported edits, reject a
source with a real ERC fault, and exercise rollback. Only the Ethernet PNG changes;
Main remains identical. Manufacturing outputs match except their creation-time
comment and derived MD5 checksum; all geometry/other bytes match.

The installed Codex host also created a candidate and received its actual edited
Ethernet image, which this agent inspected. Host testing uses direct MCP calls in
an ephemeral thread, not a model turn or persistent MCP configuration change.
See `evidence/2026-09-11-day4/README.md` for exact runs and limitations.

## Lifecycle, rollback and limits

Candidate handles are session-scoped and track both original-source and candidate
revisions. Saving a candidate in the GUI may add/change preferences, invalidating
its handle. Copy a closed candidate into an allowed project folder to open it as
a new source in another session; the server does not accept arbitrary paths into
its own data directory. Do not remove or modify data used by an active operation.

Rollback means abandoning the separate candidate. The acceptance harness closes
its MCP process, verifies the exact owned candidate's absolute path and closed
saved contents, removes only that copy, and reopens the untouched original at
1.5 kΩ through a fresh MCP client. No rollback/deletion tool is exposed to models.

Validation uses several sequential CLI calls. The generated experimental config
allows **300 seconds** per tool, with the default **30-second per-invocation** CLI
timeout. Increasing the latter may require increasing the host timeout. The
operation has no separate total deadline yet. Retention, disk quotas and general
process-tree supervision remain Day 5 reliability work. Cooperative revision
checks do not provide an atomic transaction against an adversarial writer.

## Sources and resolved findings

- [Typed resistance and display units](https://github.com/LibrePCB/LibrePCB/blob/2.1.1/libs/librepcb/core/attribute/attrtyperesistance.cpp), [attribute serialization](https://github.com/LibrePCB/LibrePCB/blob/2.1.1/libs/librepcb/core/attribute/attribute.cpp).
- [CLI save/strict interface](https://librepcb.org/docs/cli/open-project/), verified by real executions.
- [GUI environment settings](https://github.com/LibrePCB/LibrePCB/blob/2.1.1/apps/librepcb/main.cpp), [project argument handling](https://github.com/LibrePCB/LibrePCB/blob/2.1.1/libs/librepcb/editor/guiapplication.cpp), [workspace format](https://github.com/LibrePCB/LibrePCB/blob/2.1.1/libs/librepcb/core/workspace/workspace.h).
- [Gerber checksum generation](https://github.com/LibrePCB/LibrePCB/blob/2.1.1/libs/librepcb/core/export/gerbergenerator.cpp): timestamp changes also change the checksum. The initial comparison missed this metadata dependency; the corrected test preserves every other byte.
- GUI `--help` is unsupported and launches workspace selection; the exploratory
  process was terminated at its timeout. Use the verified project argument.
- Initial save validation flagged generated preference files; independent saved
  controls resolved this explicitly. An initial part-choice unit mutation changed
  another instance of the shared device; locating R17's parsed node fixed the test.
