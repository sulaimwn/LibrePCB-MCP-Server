# Instructions for coding agents

- Read STATUS.md, PLAN.md and SPEC.md before changing code. Continue the next incomplete task.
- Respect the owner's current instructions over this plan. Update the plan when scope changes.
- One writer at a time. Inspect existing changes; preserve other sessions' work.
- Implement a small Windows-first local MCP server against one verified stable LibrePCB release. Avoid premature native-fork work, routing, web UI, hosted services or multi-platform packaging.
- Verify current SDK/CLI interfaces before using them. Pin dependencies and record tool versions.
- Keep transport, domain operations and file/CLI adapters separate.
- Default to preserving source designs. Write candidate copies, respect locks and revisions, validate paths, and use argument arrays instead of shell command strings.
- Do not expose unrestricted shell/Python execution as product tools.
- Read/check/export must pass a real end-to-end test before write tools are release candidates.
- Test actual design invariants and failure modes. Never describe a mock-only test as LibrePCB integration verification.
- Keep model-facing results bounded and structured, with raw diagnostics available as artifacts.
- Update STATUS.md before stopping or handing over: files changed, checks actually run, failures, running processes and next task.
- Do not add subscription credentials or model API keys. Do not publish, deploy, or contact maintainers without an explicit user request.
- Do not claim a feature exists because it appears in SPEC.md. Planning documents describe intended behavior.
