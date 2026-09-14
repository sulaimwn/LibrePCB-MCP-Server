# Day 7 local candidate acceptance

Recorded September 14, 2026. **0.1.0rc1 passes local candidate acceptance.**
The owner accepted the sample output review and explicitly left the software
license undecided. No public software release, tag or deployment was performed.

The candidate source is commit `743e415a3bcba6b0c229173b22ec24d18c1e0cdc`.
Its immutable ZIP is 2,373,442 bytes, SHA256
`45e1c470990f7dcddf8afdf7c646af31340d0a0e9c8404b301ab494e1087ae80`.
The installed wheel SHA256 is
`cb20513bd38346a124d69ba4558f29467f3244b8c5637e4eeebaa9850e57c46a`.

| Check | Actual result |
| --- | --- |
| [Package acceptance](package-acceptance.json) | 30 checks passed over the bundle manifest, source/wheel equality, resource files, pins and repeated identical wheel build. |
| [Dirty-source refusal](dirty-source-refusal.json) | Actual builder invocation rejected the uncommitted checkout; clean-source build subsequently passed. |
| [Installed module probe](commands/isolated-module-probe.txt) | Noneditable rc1 loads from site-packages with Python isolated mode and both output-job resources present. |
| [Dependency check](commands/pip-check.txt) | No broken requirements. |
| [Default SDK workflow](default.json) | 21 checks / 10 calls, all eight tools. |
| [Experimental SDK workflow](experimental.json) | 26 checks / 12 calls, all nine tools, validated R17 candidate and unchanged original. |
| [Codex host](host.json) | 15 checks / 13 direct host calls, native images/checks/exports and edit. No model turn. |
| [Owner decisions](owner-decisions.json) | Sample output review accepted; license explicitly deferred. |

All final server/host stderr files are empty. Sample counts remain 97 components,
48 nets, one board and two schematic sheets, with 2 approved ERC / 16 approved
DRC findings and zero unapproved findings. R17 stays 1.5 kΩ in the original and
becomes 2.2 kΩ only in the candidate. Received original/candidate PNGs match the
owner-reviewed Day 6 packet; their hashes are in [summary.json](summary.json).

[The artifact map](artifact-map.json) links **120 raw CLI diagnostic files** and
**22 operation reports**. [The bundle manifest](bundle-manifest.json) records the
source revision and component hashes; [build-log.txt](build-log.txt) records the
actual initial build. Exact commands and subsequent installation/rebuild output
are retained under commands/. Paths use `<REPO>`, `<BUILD_SOURCE>` and `<USER>`;
text diagnostics normalize line endings/trailing whitespace for Git.
[Final consistency review](final-review.json) passes 27 checks over the current
and installed package, evidence, documentation, recorded decisions and process exit.
It also checks path sanitization inside the host's nested JSON text results.

The candidate was installed into an existing isolated environment. Day 6 remains
the fresh-checkout/venv/runtime trial on this same Windows machine, with 57 passing
unit/adapter tests. No new complete unit suite or all historical integration
harnesses were rerun in Day 7 because runtime behavior changed only by version.
These package checks are distinct from the actual SDK/CLI/host tests above.

Earlier evidence remains unchanged. The candidate's source archive predates this
acceptance packet; current repository documentation is the closing record, not a
claim that the immutable ZIP was rebuilt after verification. No persistent live
chat, owner-followed installation, personal-design trial or fresh Windows OS is
claimed. The server remains WIP, with experimental editing opt in.
