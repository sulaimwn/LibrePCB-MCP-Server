# Day 3 validation evidence — September 11, 2026

Package **0.1.0.dev3**, Windows 11 x64, Python 3.12.14, MCP SDK 2.2.0,
LibrePCB 2.1.1 / stable format 2. All listed acceptance results passed.
The project remains WIP; these are development compatibility results.

| Record | Result | Actual local run |
| --- | --- | --- |
| [Unit/adapter output](unit-tests.txt) | 33 passed in 17.153 s | `work/day3-unit-tests.txt`, `.venv` |
| [Inspection regression](mcp-inspection.json) | 82 checks, 27 MCP calls | `work/d2-33b330/`, editable Day 3 |
| [Checks, exports, native images](mcp-checks-exports.json) | 73 checks, 20 MCP calls | `work/d3-a225dc/`, **installed wheel**, `work/v2` |
| [Installed Codex host](codex-host.json) | 12 checks, 10 host MCP calls | `work/cx-2957d9/`, Codex 0.153.4 |
| [Eight actual schemas](tool-schemas.json) | Discovery and calls verified | Final packaged SDK run |
| [Build/environment record](build-and-environment.json) | Wheel, jobs, lock and image hashes; dependency check | Unchanged 36-dependency lock |
| [Final consistency review](final-review.json) | 30 checks passed | Documentation links, recorded assertions, source/wheel correspondence, hashes, configs and whitespace |

Unit tests include synthetic diagnostic/artifact fixtures plus actual Python
subprocess and Windows filesystem tests. Synthetic unit tests are not LibrePCB
integration. The three client reports use the real CLI and D0 reader design.

## Complete flow

- Inspection: 97 components, 48 nets, one board, two sheets. All 184 source
  files and saved-copy contents remain unchanged during MCP operations.
- Baseline: **2 approved ERC / 16 approved DRC**, zero unapproved findings.
  This does not imply electrical correctness.
- Adding a net without connected signals produces a real ERC warning naming
  `MCP_DAY3_UNCONNECTED`. Narrowing a real trace from 0.2 mm to 0.01 mm produces
  a real DRC error. Both return `outcome=violations` with one unapproved finding.
  Construction is reproducible in `scripts/day3_fixtures.py`.
- Native PNG bytes for both sheets match artifact hashes; repeat exports use
  distinct directories. PDF and 11 Gerber/Excellon artifacts pass validation.
  The installed wheel contains and uses its packaged job resources.
- Occupied output contents are preserved. Locks and unknown selectors/jobs are
  rejected. A project-owned job with an escaping output path is not executed;
  the server-owned job produces only the expected PDF.
- Ordinary and image responses have separate verified wire bounds. Unit tests
  cover unknown diagnostics, contradictions, fatal stderr, missing completion,
  Unicode expansion, tampering, invalid manifests and output flooding.

## Artifacts and normalization

[artifact-map.json](artifact-map.json) maps original paths to **90 CLI logs**
under `raw/` and **12 check reports/export manifests** under `reports/`.
Empty logs are intentional. Top-level server/host stderr files are all empty.
Repository prefixes become `<REPO>`; text is UTF-8 with LF line endings.
Identifiers, counts and diagnostics are otherwise retained. Generated binaries
are referenced by path, size and SHA256; manufacturing files, PDFs, copied
projects and runtimes remain in ignored `work/`, reproducible with the harnesses.

The actual Codex-received Main (`work/cx-2957d9/host-preview-6.png`) and
SDK-received Ethernet (`work/d3-cada83/client-preview-5.png`) were visually
inspected by this agent. The latter is committed unchanged as
[the README image](../../docs/images/d0-reader-ethernet.png). This earlier editable
run also passed 73 checks / 20 calls. The final wheel run received its own PNGs;
both sets' hashes are recorded in the build/environment record.

## Resolved failures and coverage limits

Initial validation rejected the CLI's `.librepcb-output` control file. Final
validation checks its paths, exact job UUID and complete artifact set, excluding
it from deliverables. Fixed A4 pages and static names prevent excessive preview
dimensions and project-name output paths. Final installed-wheel acceptance passed.

The Codex harness uses an ephemeral app-server thread and direct tools. No model
turn or persistent client configuration changed. Native image delivery and
subsequent agent inspection passed. UI click-through, Claude, live chat MCP
installation and an owner trial remain untested. The wheel test reused an existing
isolated dependency environment; it is not a fresh-machine trial. GUI save/reopen,
editing/rollback, other designs/locales/platforms and manufacturing correctness
remain outside these results.

Day 1/2 evidence remains unchanged history. Its older versions/tool counts describe
those checkpoints. Day 1's baseline was not rerun in Day 3. Reproduce with
[Windows setup](../../docs/WINDOWS_SETUP.md); see the
[Day 3 contract](../../docs/DAY3.md) for implemented limits and policies.
