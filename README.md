# LibrePCB-MCP-Server — WIP

**Work in progress.** This is an experimental development project, not a finished
product or an official LibrePCB integration. Interfaces and supported behavior
may change. Day 3 checks and previews are currently being implemented and tested.

A local MCP server for inspecting saved LibrePCB projects. Rule checks, previews,
manufacturing exports and a constrained edit are subsequent milestones.

## Start here

1. Read [STATUS.md](STATUS.md) for the actual state and next task.
2. Read [PLAN.md](PLAN.md) for the seven-day timeline and release criteria.
3. Read [SPEC.md](SPEC.md) for scope, architecture, and proposed tools.
4. Read [HANDOFF.md](HANDOFF.md) before switching between Claude and ChatGPT.
5. Read [RESEARCH.md](RESEARCH.md) for evidence and unresolved questions.

**Current state: Day 2 complete.** Five local MCP tools report status, open an
allowlisted saved project, summarize it, and list components and nets. The real
sample returns 97 components and 48 nets. SDK clients and the installed Codex
host passed real tool calls; the source files stayed unchanged. Package version
`0.1.0.dev2` uses Python 3.12, MCP SDK 2.2.0 and LibrePCB 2.1.1 on Windows x64.

See [Windows setup](docs/WINDOWS_SETUP.md), [Day 2 behavior and limits](docs/DAY2.md),
and [test evidence](evidence/2026-09-10-day2/README.md). Next: Day 3 MCP checks and
previews. Day 1 already proved direct CLI ERC/DRC and PNG/PDF/Gerber exports;
those operations are not MCP tools yet. No edit feature is implemented.

## Week-one objective

Ship a small, tested Windows-first local MCP release for saved LibrePCB projects: inspection, ERC/DRC, preview/export, clear errors, and reproducible setup. Include one constrained design-edit operation only if its validation gate passes. Call an unfinished result a prototype; a calendar deadline does not establish readiness.

Full schematic authoring, routing, and seamless live GUI control remain longer-term goals. Their feasibility and effort must be established with separate experiments.

## Working arrangement

The owner will alternate between ChatGPT and Claude as subscription limits require. Files in this folder, rather than either model's memory, are the source of truth. Use one writer at a time. The owner reviews actual PCB results and runs any necessary interactive desktop checks.

Open this folder as the project in the coding client. If the other client cannot access the local folder, transfer it or use a private Git repository. Do not assume a subscription includes local file access, shared conversation history, or API credits. A normal MCP tool server need not make model API calls itself.

This development repository preserves source, documentation, test fixtures,
validation evidence and project history. Downloaded tools, virtual environments,
temporary work and credentials are excluded. A software license for the server
has not yet been chosen; the included sample design has its own CC0 license.
