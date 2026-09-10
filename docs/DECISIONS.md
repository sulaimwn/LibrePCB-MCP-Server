# Implementation decisions and pitfalls

Recorded from implementation on 2026-09-10. Read alongside SPEC.md; this document states what we chose and what still needs proof.

1. **Pin portable LibrePCB 2.1.1 on Windows x64.** It is an official stable release and passed actual CLI tests. No source build or historical native binding is required. Stable project format is 2.
2. **Use Python 3.12.14 in a project venv.** The desktop supplies a usable base interpreter even though Python is not on PATH. There are no third-party Python dependencies at this milestone. Choose/pin the official MCP SDK only after verifying its current interfaces.
3. **Vendor the D0 reader archive unchanged.** It is under 1 MB, has an embedded CC0 license, already uses format 2, includes libraries and board data, and passes strict open. It has two schematic sheets and one board. This is a practical fixture, not the eventual smallest edit-demo design.
4. **Use explicit output jobs.** The fixture's existing `Schematic PDF` and `Gerber/Excellon` jobs pass. A trusted server-owned graphics job produces two small PNGs at 150 DPI. Deprecated direct schematic export returns 2 despite producing output; suppressing the warning would hide a compatibility problem.
5. **Keep transport, domain and adapter boundaries separate.** Only the internal process adapter exists today. Its arbitrary argument list is for trusted developer callers and must never be registered as an MCP tool. Domain code must provide fixed operations and enforce paths/versions/locks/revisions before calling it.
6. **Preserve approved findings in summaries.** The sample has 2 ERC and 16 DRC approvals. Zero unapproved findings does not mean no findings. Counts arrive on stdout; warning detail arrives on stderr.
7. **Exit 1 has multiple meanings.** Exposing existing ERC approvals yields exit 1; malformed S-expression syntax also yields exit 1. A process that completed with code 1 is not necessarily a crashed process. Upcoming diagnostic parsing must be conservative and retain unknown output. Do not label an unparseable result “clean.”
8. **Use the native Qt platform on Windows.** Forced offscreen mode hung version detection. The final adapter removes this override on Windows and uses a hidden console. Tests cover only the recorded Windows/en-US host.
9. **Saved state needs a deliberate consistency policy.** Upstream source shows `.lock`, `.autosave` and `.backup` semantics. The development fixture harness creates isolated fresh copies. It is not a tested solution for arbitrary live/open user projects. The upcoming `open_project` must validate containment, unsupported versions and recovery/lock state and clearly label snapshots.
10. **Read raw component values honestly.** Inspection of the real circuit file shows references such as R17 with raw value `{{RESISTANCE}}` and a separate typed resistance attribute. Do not claim raw text is the displayed electrical value or change only one field without understanding it. A structured parser must precede design edits.
11. **Development evidence is not a release gate shortcut.** No MCP client, model-facing check tool, new wiring/DRC fault fixture, live GUI save/reopen, value edit, rollback, fresh-machine install or owner review has been tested. These remain in PLAN.md.

## Things intentionally deferred

- General project parsing and library/connectivity resolution.
- Model-facing allowlists, symlink/reparse handling, locks and stale revisions.
- Arbitrary project output-job execution: jobs and substitutions can choose paths; the model-facing implementation must restrict supported types and outputs.
- Hard byte caps/retention for raw logs and artifacts. Excerpts are bounded now; the internal log files are not hard capped, though process time is finite.
- Process-tree supervision beyond killing the direct child. Current direct CLI operations completed without persistent child processes; review if future jobs can spawn children.
- Selecting a public license for our own code.

## Context preserved from the reference projects

The KiCad reference uses IPC/SWIG backends. That is architectural inspiration, not a LibrePCB API. The 2018 Python-binding fork is useful for later native undo/GUI ideas, but no code from it has been ported or used. See RESEARCH.md for exact links and limitations.
