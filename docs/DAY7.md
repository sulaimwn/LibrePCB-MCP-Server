# Day 7: local release candidate

Completed September 14, 2026 for the agreed Windows/sample scope. The owner
accepted the Day 6 output review and explicitly left the license undecided.
**0.1.0rc1 is a local WIP candidate, not a public software release.**

## What changed

Runtime behavior is unchanged from dev6 except its version. No new native API,
editing operation, route planner, hosted service or platform was added.

`scripts/build_candidate.py` requires the documented Windows/Python environment,
the installed dependency pins and a clean committed checkout. It archives the
exact commit, builds the wheel from that archived source in a short temporary
directory, compares packaged Python/job resources, and writes a local ZIP with
source, wheel, dependency lock, toolchain, install notes, changelog and release notes.
An artifact manifest and ZIP checksum identify the exact bytes. Builds retain
their source staging and logs; they do not upload files or create release tags.

The clean-source check was actually exercised before committing: the builder
refused the dirty checkout with exit 1. After checkpoint `743e415`, the build
succeeded. Building the same wheel again with the recorded SOURCE_DATE_EPOCH
produced identical bytes. Assembly alone is not runtime acceptance.

## Candidate and actual verification

Candidate directory:
`work/candidates/0.1.0rc1-743e415-f10488/`

Source revision: `743e415a3bcba6b0c229173b22ec24d18c1e0cdc`.
Bundle: `librepcb-mcp-server-0.1.0rc1-local.zip`, **2,373,442 bytes**.
SHA256: `45e1c470990f7dcddf8afdf7c646af31340d0a0e9c8404b301ab494e1087ae80`.

- **30 package checks** pass: manifest, archive contents, source/wheel resources,
  dependency pins and repeatable wheel build.
- Actual noneditable wheel installed into the existing isolated `work/v2` venv;
  dependency check and isolated site-packages/resource probe pass.
- Default generated configuration: **21 checks / 10 real MCP calls**.
- Experimental configuration: **26 checks / 12 calls**, including a validated
  R17 candidate and native image. Original files remain unchanged.
- Installed Codex 0.153.4 host: **15 checks / 13 calls**, including checks,
  exports, the edit and image delivery. No model turn or persistent config change.
- All server/host stderr files are empty. The original and edited Ethernet images
  match the owner-reviewed Day 6 images byte-for-byte.

The **57 unit/adapter tests** passed in Day 6. They were not rerun for a version
change; Day 7 verified the new package builder and complete installed workflows.
Earlier integration, GUI save/reopen and rollback evidence remains unchanged.
See [Day 7 evidence](../evidence/2026-09-14-day7/README.md) and
[release notes](../RELEASE_NOTES.md) for scope and limits.

## Evidence and continuation

The immutable candidate uses the implementation commit above. Its acceptance
record is a separate sidecar, and the final documentation/evidence commit comes
later. Historical STATUS/README in source.zip describe the state at build time;
current STATUS.md and the Day 7 packet record completed acceptance. No candidate
was silently rebuilt after testing to include later documentation.

The initial seven milestones now have a local candidate for the included sample.
Persistent live-chat setup, another design, fresh Windows-machine installation,
broader format coverage and native live-editor work remain separate tasks.
Start with the prepared client snippets and another inspection/check/export trial
before expanding editing. The owner chose no license for now; no public release
or deployment is authorized. Continue preserving context and private GitHub pushes.
