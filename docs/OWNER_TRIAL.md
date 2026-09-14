# Try the sample and review its outputs

This WIP supports saved projects with LibrePCB 2.1.1 on Windows. The default
configuration has eight inspection/check/export tools. Resistor editing is a
separate, opt-in experiment and always creates a candidate copy.

## Generate and check a sample

After following [Windows setup](WINDOWS_SETUP.md), run:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_demo.py --verify
```

For the optional resistor edit demonstration, add `--experimental-edits`.
The command creates a new sample, client snippets and prompt under `work/demo-<id>/`.
It then uses the actual generated configuration to start a real MCP client/server,
inspect the sample, run checks, obtain a native schematic image and export PDF
and manufacturing files. No model API call or client-setting change is required.

The printed `review_directory` contains `REVIEW.md`, the original schematic PDF,
actual PNG previews, a full result report and server stderr. With editing enabled,
the review includes the candidate image and saved project path. You can open the
closed `.lpp` in LibrePCB to inspect it yourself. Source files remain unchanged.

Expected sample results: **97 components, 48 nets, one board, two sheets**;
**2 approved ERC / 16 approved DRC findings**, zero unapproved findings. In the
editing demonstration, R17 changes **1.5 kΩ → 2.2 kΩ** only in the candidate.
Check results describe this fixture; they are not manufacturing approval.

## Connect your client

The parent demo directory contains `codex-config.toml`,
`claude-desktop-config.json` and `sample-prompt.txt`. Review the generated absolute
paths and preserve your existing client settings when adding the server entry.
The default allows access only to that demo's sample directory and puts snapshots
and exports in its separate data directory.

For Codex, add the generated `[mcp_servers.librepcb]` table to a trusted project's
`.codex/config.toml` or the appropriate user configuration, then restart the MCP
connection/client. Open a new conversation and use `sample-prompt.txt`.
The server needs no sign-in or model API key of its own. See
[official Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).
The standalone checker proves the configured command works; it does not prove
your live chat has loaded that entry. Claude connection remains optional/untested.

## What to review

1. Is the original schematic readable, and can you open its PDF?
2. If editing is enabled, does R17 show 2.2 kΩ in the candidate and 1.5 kΩ in the
   original? Are the surrounding connections unchanged?
3. Does the client find LibrePCB's tools and complete the sample prompt?
4. Is any setup instruction confusing or any output missing?

The agent can prepare and test these outputs; owner acceptance remains pending
until you have inspected them. A personal-design trial is separate from this
included CC0 sample. Save and close a personal design before opening it through
the server, and configure only its intended project root.

To retry a failed sample check, run `verify_demo.py --demo <absolute demo path>`;
it creates a new review directory. Retain wanted candidates, and clean only
inactive session data after the server and LibrePCB processes have exited.
See [Day 5 recovery limits](DAY5.md).
