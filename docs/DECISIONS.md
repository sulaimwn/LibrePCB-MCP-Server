# Implementation decisions and pitfalls

Recorded from implementation through 2026-09-11. Read alongside SPEC.md; this document states what we chose and what still needs proof.

1. **Pin portable LibrePCB 2.1.1 on Windows x64.** It is an official stable release and passed actual CLI tests. No source build or historical native binding is required. Stable project format is 2.
2. **Use Python 3.12.14 and official MCP SDK 2.2.0 in a project venv.** Installed source and current official interfaces were verified. Pin all 36 runtime/build dependencies with Windows/Python 3.12 wheel hashes. Use hatchling 1.32.0 plus editables 0.6 for repeatable editable installs.
3. **Vendor the D0 reader archive unchanged.** It is under 1 MB, has an embedded CC0 license, already uses format 2, includes libraries and board data, and passes strict open. It has two schematic sheets and one board. This is a practical fixture, not the eventual smallest edit-demo design.
4. **Use explicit output jobs.** The fixture's existing `Schematic PDF` and `Gerber/Excellon` jobs pass. A trusted server-owned graphics job produces two small PNGs at 150 DPI. Deprecated direct schematic export returns 2 despite producing output; suppressing the warning would hide a compatibility problem.
5. **Keep transport, domain and adapter boundaries separate.** Day 2 implements the three layers. The internal runner's arbitrary argument list is for trusted developer callers and is never an MCP tool. Domain operations select fixed CLI invocations and enforce paths/versions/locks/revisions.
6. **Preserve approved findings in summaries.** The sample has 2 ERC and 16 DRC approvals. Zero unapproved findings does not mean no findings. Counts arrive on stdout; warning detail arrives on stderr.
7. **Exit 1 has multiple meanings.** Exposing existing ERC approvals yields exit 1; malformed S-expression syntax also yields exit 1. A process that completed with code 1 is not necessarily a crashed process. Day 3 parsing cross-checks exact stdout structure, counts, stderr findings and completion/exit status; unknown output becomes an indeterminate error. Do not label an unparseable result “clean.”
8. **Use the native Qt platform on Windows.** Forced offscreen mode hung version detection. The final adapter removes this override on Windows and uses a hidden console. Tests cover only the recorded Windows/en-US host.
9. **Require closed saved projects.** Day 2 rejects any `.lock`, `.autosave` or `.backup` entry, creates a byte-preserving copy, validates it with LibrePCB, and checks source/copy revisions before results. Local allowlisted paths reject links/junctions, hardlinks, traversal and unsupported formats. This is not atomic against adversarial concurrent filesystem changes or access to unsaved GUI state.
10. **Read raw component values honestly.** Inspection of the real circuit file shows references such as R17 with raw value `{{RESISTANCE}}` and a separate typed resistance attribute. Do not claim raw text is the displayed electrical value or change only one field without understanding it. A structured parser must precede design edits.
11. **Development evidence is not a release gate shortcut.** SDK clients and the installed Codex host pass all eight tools, real ERC/DRC faults, native PNG, PDF and manufacturing exports. Host-received images were visually inspected. Live GUI save/reopen, value edits, rollback, fresh-machine install, Claude/UI connection and owner review still need their gates in PLAN.md.
12. **Use compact storage paths on Windows.** Long generated fixture paths failed at extraction. Short run/session/snapshot directory names and an explicit path-length rejection avoid changing system settings.
13. **Return a bounded projection, preserve the original bytes.** The S-expression parser retains spans and accepts only the documented inspection subset. It does not serialize designs or resolve display templates. Ordinary results have text plus structured data, matching error flags and a 64,000-byte cap; lists use size-aware pagination. Native PNG results have a separate 1,500,000-byte wire cap. See `docs/DAY2.md` and `docs/DAY3.md`.

14. **Separate ERC and selected-board DRC invocations.** This gives reliable attribution across stdout/stderr. Use a verified board UUID mapped to `--board-index`; require selection for multiple boards.
15. **Validate LibrePCB output bookkeeping.** The CLI emits `.librepcb-output`; check exact job UUID and relative artifact set, then exclude it from deliverables. Initial validation failed until this verified control file was handled.
16. **Deliver actual image bytes.** `export_preview` attaches one native SDK `ImageContent`, rehashing the registered file first. The installed Codex host passes through usable PNGs; this agent inspected them. This is not a live model-turn or UI test.
17. **Publish the requested WIP repository.** The owner explicitly asked for GitHub upload. Use the stated private default, keep complete project history and evidence, exclude runtimes/secrets/scratch copies, and retain the pending license decision before any public software release.

## Things intentionally deferred

- General geometry parsing, assembly/display-value resolution and a design serializer.
- Arbitrary project output-job execution remains excluded. Day 3 uses packaged server-owned jobs, fixed filenames and a validated board UUID; project/variant metadata cannot choose paths.
- Automatic retention and runtime filesystem quotas. Day 3 hard-caps raw logs at 2 MB per stream and post-validates export totals at 32 MB / 64 files; snapshots/artifacts still need manual inactive-session cleanup.
- Process-tree supervision beyond killing the direct child. Current direct CLI operations completed without persistent child processes; review if future jobs can spawn children.
- Selecting a public license for our own code.

## Context preserved from the reference projects

The KiCad reference uses IPC/SWIG backends. That is architectural inspiration, not a LibrePCB API. The 2018 Python-binding fork is useful for later native undo/GUI ideas, but no code from it has been ported or used. See RESEARCH.md for exact links and limitations.
