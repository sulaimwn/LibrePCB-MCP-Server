# LibrePCB MCP Server

A local, open-source tool that lets an MCP-compatible AI client inspect LibrePCB projects, run checks, produce previews and manufacturing files, and eventually make validated design edits.

## Start here

1. Read [STATUS.md](STATUS.md) for the actual state and next task.
2. Read [PLAN.md](PLAN.md) for the seven-day timeline and release criteria.
3. Read [SPEC.md](SPEC.md) for scope, architecture, and proposed tools.
4. Read [HANDOFF.md](HANDOFF.md) before switching between Claude and ChatGPT.
5. Read [RESEARCH.md](RESEARCH.md) for evidence and unresolved questions.

**Current state:** planning workspace only. No MCP implementation, LibrePCB installation verification, runtime tests, or working editing demo has been completed.

## Week-one objective

Ship a small, tested Windows-first local MCP release for saved LibrePCB projects: inspection, ERC/DRC, preview/export, clear errors, and reproducible setup. Include one constrained design-edit operation only if its validation gate passes. Call an unfinished result a prototype; a calendar deadline does not establish readiness.

Full schematic authoring, routing, and seamless live GUI control remain longer-term goals. Their feasibility and effort must be established with separate experiments.

## Working arrangement

The owner will alternate between ChatGPT and Claude as subscription limits require. Files in this folder, rather than either model's memory, are the source of truth. Use one writer at a time. The owner reviews actual PCB results and runs any necessary interactive desktop checks.

Open this folder as the project in the coding client. If the other client cannot access the local folder, transfer it or use a private Git repository. Do not assume a subscription includes local file access, shared conversation history, or API credits. A normal MCP tool server need not make model API calls itself.

The project has not been published and a software license has not yet been chosen. Never describe it as an official LibrePCB integration.
