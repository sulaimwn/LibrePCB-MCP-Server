# Current project status

Updated September 15, 2026, America/Toronto. **Codex remains the active writer.**
The owner requested continued work, detailed folder context and regular GitHub
pushes. No Claude handoff is planned. Days are milestones, not elapsed dates.

## Milestone

**Days 1–7 complete for the agreed sample scope: local WIP candidate 0.1.0rc1.**
The owner accepted the sample REVIEW.md and explicitly left the license undecided.
Package **0.1.0rc1**, Windows x64, Python 3.12.14, MCP SDK 2.2.0,
LibrePCB 2.1.1 / stable format 2 / revision 06465bf. The 36-dependency hash lock
is unchanged. Eight default tools; opt-in ninth `create_value_edit`. Still WIP.

GitHub: [sulaimwn/LibrePCB-MCP-Server](https://github.com/sulaimwn/LibrePCB-MCP-Server),
**private**, `origin`, branch `master`. Regular pushes are authorized. Day 5 ended
at `e488b1c`; Day 6 implementation was pushed as `718c50d`. `git log -1` identifies
the final documentation/evidence checkpoint. This is development publication.

## Live Codex chat verified September 15

The owner's connected Codex conversation now exposes all eight default tools.
Nine recorded live calls covered status, opening the sample, summary, both pages
of components, nets, ERC/DRC, native Ethernet PNG and schematic PDF. All succeeded:
97 components, 48 nets, two sheets and one board; 2 approved ERC / 16 approved DRC
findings, zero unapproved findings. The native image was displayed and visually
inspected in this chat. Three exported files match their returned hashes/sizes;
the image attachment matches the selected PNG. All 184 source files retain the
opening revision. This is an actual model-led conversation, beyond the earlier
SDK and direct-host tests. Editing is disabled in this live connection.

Evidence: [live-chat packet](evidence/2026-09-15-live-chat/README.md), with structured
results, verification and 25 diagnostic files. No server code, dependency or
configuration changes; no new unit-suite run. Updated STATUS, PLAN, README,
HANDOFF, owner-trial and environment notes. No failed calls in this walkthrough.
The immutable Day 7 candidate and historical evidence remain unchanged.

## Day 7 changes and actual results

`scripts/build_candidate.py`, `CHANGELOG.md` and `RELEASE_NOTES.md` added.
The builder archives a clean exact commit, builds/compares the wheel, and creates
a local ZIP with source, dependencies, notes and a SHA256 manifest. Version rc1
is the only runtime change from dev6. README, plan/spec, environment/setup,
owner-context and continuity notes are current; `docs/DAY7.md` records details.

Candidate: `work/candidates/0.1.0rc1-743e415-f10488/`.
Source commit: `743e415a3bcba6b0c229173b22ec24d18c1e0cdc` (already pushed).
ZIP: `librepcb-mcp-server-0.1.0rc1-local.zip`, 2,373,442 bytes, SHA256
`45e1c470990f7dcddf8afdf7c646af31340d0a0e9c8404b301ab494e1087ae80`.
The immutable candidate predates the final documentation/evidence checkpoint;
its separate acceptance sidecar identifies the exact tested artifact.

| Day 7 check | Actual result |
| --- | --- |
| Package/source/manifest/rebuild | **30 checks passed**, including identical repeated wheel build and exact committed source/resource bytes. |
| Noneditable installation | Actual candidate installed in `work/v2`; `pip check` and isolated site-packages/resource probe passed. |
| Default sample through generated configuration | **21 checks / 10 real MCP calls passed**; `work/demo-d9c0ce/review-b776e1/`. |
| Experimental sample | **26 checks / 12 calls passed**; `work/demo-3be0de/review-2b5012/`. |
| Installed Codex 0.153.4 host | **15 checks / 13 calls passed**, experimental edit/image included; `work/cx-aa6633/`. |
| Source/image preservation | Originals unchanged; final original/candidate previews exactly match the owner-reviewed Day 6 packet. All server/host stderr is empty. |
| Dirty-source guard | Actual uncommitted-checkout build refused with exit 1; after commit the candidate built successfully. |
| Final consistency review | **27 checks passed** over current/installed package bytes, evidence, pins, documentation, recorded decisions and process exit. |

Evidence: [Day 7 packet](evidence/2026-09-14-day7/README.md), including 120 raw
CLI logs and 22 operation reports. The 57 unit/adapter tests last passed in Day 6;
no runtime behavior changed except the version, so Day 7 reran installed workflows
and package checks rather than claiming a new complete unit suite.

## Day 6 historical changes/results

The following rows describe the completed dev6 trial; earlier evidence is unchanged.

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
noneditable dev6 wheel. Day 7 updated main `.venv` to editable rc1 and `work/v2`
to the actual noneditable rc1 candidate; the Day 6 temporary trial remains dev6.

## Owner review and boundaries

Ready packet: `work/demo-e8a9b4/review-fb79f0/REVIEW.md`; generated config and
prompt are in its parent demo directory. Outputs were offered for review in this
thread. **The owner accepted this sample output review on September 14.**
See `docs/OWNER_TRIAL.md`. The owner explicitly leaves the software license
undecided for now; this does not block the local private candidate trial.
The connected Codex chat passed the September 15 sample workflow. Claude,
personal-design trials and a fresh Windows machine remain unverified. This
walkthrough did not edit persistent client settings or inspect credentials.

Closed saved projects only; narrow typed-resistance candidates, no source
replacement or general editing. No placement, wiring, routing or live-editor API.
Day 5 cooperative deadlines/direct-child cleanup and manual inactive-session
retention still apply; no process-tree guarantee or automatic disk quota.
No model API calls/keys, credential changes, maintainer contact or deployment.

## Running processes

The host-managed LibrePCB MCP connection used by this chat remains active;
session data is in `work/demo-d9c0ce/d/s-c0bf9bf17d48/`. Do not stop it or clean
its files during the conversation. All requested checks/exports have returned.
The Day 7 no-processes record describes that earlier test's shutdown only.

## Next task — client usability and broader inspection, Codex continues

1. Read AGENTS/STATUS/PLAN/SPEC and Day 7 evidence; inspect Git. Use one writer.
2. The live Codex sample connection is verified; preserve the active connection.
   Read `evidence/2026-09-15-live-chat/README.md` for results and artifact locations.
   Restart/reconnection behavior and live experimental editing were not tested.
3. Validate another redistributable design through inspection/check/export before
   broadening editing. Personal designs need an explicitly provided local path.
4. Follow the after-week-one roadmap only within verified scope. No general
   editing, placement/routing or native GUI API has been implemented.
5. Leave the license undecided per the owner. Keep the candidate local/private;
   no public release, deployment or maintainer contact is authorized. Continue
   meaningful private GitHub pushes and keep actual results/context current.
