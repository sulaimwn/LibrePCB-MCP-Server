# Actual Codex live-chat sample workflow

September 15, 2026, America/Toronto (tool timestamps cross into September 16 UTC).
The owner requested a live `get_status` check and then authorized the sample
walkthrough with “go ahead”. These are actual LibrePCB MCP tool calls made by
Codex in the owner's conversation, not a replay or direct-host test harness.

## Results

- Server 0.1.0rc1, MCP SDK 2.2.0, LibrePCB CLI 2.1.1 / stable format 2.
- All eight default tools succeeded in nine recorded calls; components required
  two pages (68 + 29), despite requesting a limit of 100, due to response bounds.
- Complete inspection: 97 components, 48 nets, one board, two schematic sheets.
- ERC: 2 approved findings; DRC: 16 approved findings; zero unapproved findings.
- Native MCP Ethernet image displayed and visually inspected: circuit, title
  block and R17 1.5 kΩ visible. Both PNG sheets and the PDF exported successfully.
- All three output hashes/sizes verified; attached image bytes match the selected
  PNG. The 184-file source fingerprint matches its opening revision after exports.
- Editing disabled. No source modifications, dependency changes, server changes,
  fresh installation, restart/reconnection or live editing trial performed.
- No failed recorded calls. No new unit-suite run; historical tests stay historical.

`tool-results.json` retains all nine structured responses. `verification.json`
records follow-up file/hash checks. `diagnostics/` retains 25 CLI logs/operation
reports; `artifact-map.json` maps sanitized copies to original local artifacts
and original-byte hashes. The logs also include the preceding status call.
Machine paths are replaced with `<REPO>`/`<USER>`; image base64 is omitted.
Generated binary exports remain local, with their hashes in these records.

## Local artifacts and continuity

Source: `work/demo-d9c0ce/p/d0-reader.lpp`.
Active session: `work/demo-d9c0ce/d/s-c0bf9bf17d48/`.
Project handle: `888426709f6c420d854c3189f8bf6f66` (valid only in this server session).
Ethernet preview: `r002/files/schematic2.png`; Main: `r002/files/schematic1.png`.
PDF: `r003/files/schematic.pdf`.

The host-managed MCP process is still serving this conversation. Do not terminate
it or remove active session data. No persistent client configuration or credentials
were edited during this walkthrough. The immutable Day 7 candidate is unchanged.
This establishes live sample connectivity, not arbitrary-design compatibility,
electrical correctness or public release readiness. Claude remains untested.

Next engineering work: a second redistributable fixture for broader saved-project
inspection before expanding edits. Personal designs require an owner-provided path.
