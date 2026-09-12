# Seven-day delivery plan

Planning baseline: September 10–16, 2026, America/Toronto. Treat these as Day 1–7 milestones if the start shifts. Work proceeds in active coding sessions; this document does not schedule unattended runs.

## Capacity and scope

Owner update, September 11: Codex continues Day 4 and necessary supporting work,
with regular meaningful pushes to the existing private GitHub repository. No
Claude handoff is planned. First prove one saved-copy resistor edit and its
reopen/save/reopen, invariant, check, visual and rollback gates. Native live-editor
control remains a later investigation, not a dependency of this milestone.

Owner update, September 10: Codex continues Day 3. Upload the project to GitHub
as `LibrePCB-MCP-Server` with an explicit WIP README. This is a development
repository, not a release or deployment; retain all existing acceptance gates.

Reserve approximately 30–45 focused project hours across the week as a planning assumption, not a commitment from the owner. This includes setup, implementation, testing, and documentation. Owner time is especially needed for installation issues and reviewing LibrePCB designs. AI output must still be tested.

Earlier exploratory estimates were 40–100 hours for a general inspection/export MVP and another 100–250 hours for robust limited editing. This week's shorter plan reduces scope to one OS, one stable LibrePCB version, small fixtures, and a small tool set. It does not promise the same breadth sooner. At lower availability, preserve the quality gates and extend the dates.

| Day | Focus | Work and evidence required | Budget |
| --- | --- | --- | --- |
| 1 — Sep 10 | Prove the environment | Record OS, Python, stable LibrePCB and CLI versions. Select one small redistributable project; record its origin/license. Run CLI help, load it, run ERC/DRC, and generate one preview. Record exact commands, results, and baseline findings. | 4–6 h |
| 2 — Sep 11 | Connect MCP | Build local Python server with version/status and allowlisted project-opening tools. Test a real MCP handshake and tool call from the first client. Establish timeout/error handling. Read project metadata, component values, and nets using a real parser. | 4–6 h |
| 3 — Sep 12 | Checks and previews | Add check runner and preview/output-job tools. Return structured summaries and preserve raw reports. Test a clean fixture and deliberately introduced ERC/DRC violations. Confirm model can consume the generated preview in the chosen client. | 5–7 h |
| 4 — Sep 13 | Prove one edit | On a closed disposable copy, change one existing resistor value. Preserve identifiers and other content. Reopen, verify the value in LibrePCB, rerun checks, preview and export. Record the change and exercise rollback. No adding components or routing. | 5–7 h |
| 5 — Sep 14 | Reliability | Test locked projects, stale snapshots, malformed files, missing binaries, timeouts, unsafe paths, export collisions, and rejected edits. Harden only tools in scope. Keep continuation instructions reviewable; the owner deferred switching to Claude, so a live client switch is optional. | 5–7 h |
| 6 — Sep 15 | Package and user trial | Package/install into a fresh environment. Write and follow the Windows quickstart. Run the complete user workflow and have the owner inspect outputs. Attempt a second MCP client only if available without blocking release. | 4–6 h |
| 7 — Sep 16 | Release candidate | Resolve release-blocking bugs, rerun affected checks and one end-to-end demo, record supported versions, known limits and changelog. Produce a local release candidate with test evidence. Publish only when explicitly requested. | 3–6 h |

## Decision gates

### Milestone progress (updated September 11)

- [x] Day 1: Python 3.12.14 and portable LibrePCB 2.1.1 verified. Pinned CC0 D0 reader fixture. Real strict load, ERC/DRC, PDF/Gerber and PNG output jobs passed. Byte preservation and two negative probes passed. See `evidence/2026-09-10-day1/`.
- [x] Day 2: SDK 2.2.0 and dependencies pinned; five STDIO inspection tools; allowlisted saved copies and revisions; format-2 parser. SDK integration passed 82 checks/27 calls, installed Codex host passed 7 checks, and 19 adapter/parser/file tests passed. Fresh Python environment verified. See `evidence/2026-09-10-day2/`. No Claude/UI connection claimed.
- [x] Day 3: eight tools with conservative checks, real ERC/DRC faults, native PNG, PDF and manufacturing exports. Packaged SDK run: 73 checks/20 calls; inspection regression: 82/27; Codex host: 12/10; unit/adapter tests: 33. Host-delivered image bytes were visually inspected by this agent; no live model turn or UI connection claimed. See `evidence/2026-09-11-day3/`. Private GitHub repository created with WIP README; not a release.
- [x] Day 4: one typed-resistance candidate, real CLI and GUI save/reopen, exact design invariants, unchanged findings, previews/exports and actual discard/reopen rollback. Opt-in ninth MCP tool; 42 unit/adapter tests, 103 SDK checks/30 calls, 82 inspection checks/27 calls, 15 Codex host checks/13 calls. See `evidence/2026-09-11-day4/`.
- [ ] Day 5 in progress: cooperative deadlines/cancellation, failed-handle cleanup, report-storage failure handling and interrupted/retried operations; real recovery and packaged regressions running.
- [ ] Days 6–7: fresh-machine packaging/setup, owner trial and release candidate remain pending.

### Acceptance gates

- End of Day 1: if loading/check/export is blocked, resolve that first; do not build wrappers around assumed CLI behavior.
- End of Day 2: if structured project parsing is too broad, support a documented subset and reject unsupported versions/shapes. Do not silently misread designs.
- End of Day 3: demonstrate a useful read/check/export workflow before adding writes.
- End of Day 4: if editing fails reopening, semantic checks, or rollback, remove it from the release. Keep the experiment separately documented.
- Day 5 onward: freeze features. Reliable inspection/check/export is an acceptable week-one release; incomplete routing is not a substitute.
- A release needs passing gates, not just seven elapsed days. Record any remaining failures and extend the schedule when necessary.

## Definition of done

- Install from the project's own instructions into a clean environment on the documented Windows/Python/LibrePCB combination.
- Connect through a real MCP client and demonstrate project summary, components/nets, rule checks, and preview/export.
- Preserve a source fixture unchanged during read/check/export operations; put exports in designated output folders.
- Distinguish a design-rule failure from a process crash, malformed project, timeout, or unavailable executable.
- Reject unsupported file-format versions rather than silently modifying them.
- Include automated adapter/tool tests plus a recorded real LibrePCB end-to-end run. Mock-only tests do not prove compatibility.
- If writes ship: a closed-project value edit passes reopen/save/reopen, connectivity invariants, checks comparison, visual inspection, rollback, and stale-input tests.
- Document limitations and failure recovery. No claim of electrical correctness solely because ERC/DRC passes.
- Keep STATUS.md, HANDOFF.md, setup instructions, and test evidence current.

## After week one

1. Broaden project-format coverage and add fixtures before expanding edits.
2. Add placement of existing unconnected components; connected placement requires an explicit policy for existing traces.
3. Add library generation, component insertion, and schematic wiring with identifier/connectivity validation.
4. Investigate native editing on current LibrePCB: move one footprint pad in the open library editor and undo it. Reuse ideas from the 2018 fork, not assumptions about compatibility.
5. Extend a successful native bridge to project operations, with GUI-thread dispatch, undo groups, state revisions, and IPC lifecycle handling.
6. Treat routing and autonomous board design as separate substantial projects with their own acceptance examples.
