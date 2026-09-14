# Current project status

Updated September 14, 2026, America/Toronto. **Codex remains the active writer.**
The owner requested continued work, detailed folder context and regular GitHub
pushes. No Claude handoff is planned. Days are milestones, not elapsed dates.

## Milestone

**Days 1–6 complete for the sample scope. Day 7 local candidate is in progress.**
The owner accepted the sample REVIEW.md and explicitly left the license undecided.
Package **0.1.0rc1** is being prepared, Windows x64, Python 3.12.14, MCP SDK 2.2.0,
LibrePCB 2.1.1 / stable format 2 / revision 06465bf. The 36-dependency hash lock
is unchanged. Eight default tools; opt-in ninth `create_value_edit`. Still WIP.

GitHub: [sulaimwn/LibrePCB-MCP-Server](https://github.com/sulaimwn/LibrePCB-MCP-Server),
**private**, `origin`, branch `master`. Regular pushes are authorized. Day 5 ended
at `e488b1c`; Day 6 implementation was pushed as `718c50d`. `git log -1` identifies
the final documentation/evidence checkpoint. This is development publication.

## Day 6 changes

Day 7 in progress: `scripts/build_candidate.py` assembles an exact committed
source archive, wheel, dependency pins, release notes and SHA256 manifest into an
ignored local bundle. `CHANGELOG.md` and `RELEASE_NOTES.md` added; version rc1;
no runtime behavior change. A clean-source build and packaged MCP/host acceptance
are still required. Day 6 results below remain historical dev6 evidence.

- `scripts/bootstrap.ps1`, new `scripts/check_python.py`: check Python 3.12 x64
  before installation; use the running PowerShell edition's built-in modules;
  download into a unique partial file and accept only the pinned hash; verify
  CLI signature/version; restore the process Qt setting. The quickstart uses
  process-only RemoteSigned, without a registry policy change.
- `scripts/prepare_demo.py`, new `scripts/verify_demo.py`: validate installed
  package versions, generate client snippets, optionally exercise their literal
  command/arguments from another working directory, and leave actual previews,
  a PDF, raw report and `REVIEW.md`. Source designs stay unchanged.
- `pyproject.toml`, package `__init__.py`, `toolchain.json`: version dev6.
  Domain, transport and CLI adapter behavior otherwise unchanged from Day 5.
- README, setup, `docs/DAY6.md`, `docs/OWNER_TRIAL.md`, environment, plan,
  specification and continuity notes updated. New evidence packet below.

## Checks actually performed

All commands and raw diagnostics: [Day 6 evidence](evidence/2026-09-14-day6/README.md).

| Check | Actual result |
| --- | --- |
| Fresh private GitHub clone | Commit `718c50d1ba99e069822d8786c4d4b8528471a8f6`; no venv/runtime initially; path contains a space. |
| Fresh bootstrap | Passed: new 85,142,354-byte download, pinned hash, valid executable signature, exact CLI version, new venv, 36 locked dependencies, package and `pip check`. |
| Default generated configuration | **21 checks / 10 MCP calls passed**, all eight tools. |
| Experimental generated configuration | **26 checks / 12 calls passed**, all nine tools including validated R17 candidate. |
| Repeat bootstrap | Passed, preserving all **1258** existing demo files byte-for-byte. |
| Fresh-environment unit/adapter tests | **57 passed**, 129.657 seconds. Synthetic cases are distinct from real integration. |
| Noneditable dev6 wheel | Installed into the fresh environment; site-packages module and packaged output-job resources verified; `pip check` passed. |
| Installed wheel sample workflow | **26 checks / 12 real MCP calls passed**, including native PNG, PDF, 11 manufacturing files and validated candidate. |
| Prerequisite/cache failures | **2 passed**: missing Python creates no work/venv; corrupt cache is rejected and retained. |
| Main-workspace sample | **26 checks / 12 calls passed** at `work/demo-e8a9b4/review-fb79f0/`; original and candidate images visually inspected. |
| Final consistency review | **65 passed**: current source/wheel, pins, evidence, links, path sanitization and completed process cleanup. |

Every final demo server stderr is empty. All 184 source files remain unchanged;
97 components, 48 nets, one board and two sheets. Checks retain 2 approved ERC /
16 approved DRC findings, zero unapproved findings. R17 is 1.5 kΩ in the original
and 2.2 kΩ in the validated candidate. Packaged images match the visually reviewed
workspace images byte-for-byte. No fresh GUI save/reopen was needed for packaging;
Day 4 remains that historical evidence.

Day 5's noneditable dev5 regression evidence remains unchanged: 57 unit/adapter
tests, reliability 38 checks, inspection 82, exports/faults 73, edit/rollback 103,
Codex host 15. See `evidence/2026-09-12-day5/`. No claim those entire integration
harnesses were rerun in Day 6; the generated-config workflows above were rerun.

## Actual failures and recovery

The first fresh checkout (`lp-d6-425da4`) hit Restricted script policy. A retry
using process-only RemoteSigned started its download but the host aborted it
after 77,283,328 bytes. The old installer left an incomplete final-name ZIP.
Both logs/files are retained. The revised installer verifies a unique partial
before accepting it; the final fresh download passed. One prerequisite test
initially exposed PowerShell 7 module paths inherited by Windows PowerShell 5.1;
explicit built-in module imports fixed that. Final negative tests pass.

Final trial is retained at
`C:/Users/vboxuser/AppData/Local/Temp/lp-d6-c6010a/LibrePCB trial`.
This is a fresh checkout/environment on the **same Windows machine**, with the
existing base Python, certificate store and pip download cache. It is not a fresh
Windows installation or an owner-followed trial. The trial venv now contains the
noneditable dev6 wheel; main `.venv` remains editable dev6; `work/v2` remains dev5.

## Owner review and boundaries

Ready packet: `work/demo-e8a9b4/review-fb79f0/REVIEW.md`; generated config and
prompt are in its parent demo directory. Outputs were offered for review in this
thread. **The owner accepted this sample output review on September 14.**
See `docs/OWNER_TRIAL.md`. The owner explicitly leaves the software license
undecided for now; this does not block the local private candidate trial.
Persistent Codex UI configuration, Claude connection, personal-design trial and
a fresh Windows machine remain unverified. No persistent client config changed.

Closed saved projects only; narrow typed-resistance candidates, no source
replacement or general editing. No placement, wiring, routing or live-editor API.
Day 5 cooperative deadlines/direct-child cleanup and manual inactive-session
retention still apply; no process-tree guarantee or automatic disk quota.
No model API calls/keys, credential changes, maintainer contact or deployment.

## Running processes

All setup and sample verification commands have completed. The final read-only
process check found no owned Python setup/MCP, Windows PowerShell or LibrePCB
process remaining. Retained trial/demo folders are available for inspection;
other desktop sessions were not stopped. See the Day 6 evidence process record.

## Next task — Day 7, Codex continues

1. Read AGENTS/STATUS/PLAN/SPEC and Day 6 evidence; inspect Git. Keep one writer.
2. Finish the clean-source local candidate build and validate archive hashes,
   exact source/wheel contents and packaged output-job resources.
3. If a live client trial is wanted, use the prepared configuration and sample
   prompt. Keep SDK/host automation distinct from a persistent live chat test.
4. Install and verify the actual candidate wheel through the complete sample
   and installed Codex host. Record exact results and finalize release notes.
   License remains undecided by owner choice; no public release or deployment
   is authorized. Keep experimental editing labeled and opt in.
5. Continue meaningful private GitHub pushes and maintain this context packet.
